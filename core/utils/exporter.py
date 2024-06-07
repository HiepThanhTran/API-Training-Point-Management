import csv
import os

import unidecode
from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Table, TableStyle

from core import settings
from core.utils import dao
from core.utils.configs import CONTENT_TYPE_BY_FILE_FORMAT

font_path = os.path.join(settings.BASE_DIR, "static/fonts/dejavu/DejaVuSans.ttf")
pdfmetrics.registerFont(TTFont(name="DejaVuSans", filename=font_path))


def export_statistics(semester=None, faculty=None, sclass=None, file_format="csv"):
	students_summary_list = dao.get_statistics(semester=semester, faculty=faculty, sclass=sclass)[1]
	if faculty and not sclass:
		title_text = f"Thống kê điểm rèn luyện<br/>Khoa {faculty.name} học kỳ {semester.short_name} năm học {semester.academic_year}"
		faculty_name = unidecode.unidecode(faculty.name).lower().replace(" ", "")
		filename = f"{faculty_name}_{semester.code}_statistics.{file_format}"
	else:
		title_text = f"Thống kê điểm rèn luyện<br/>Lớp {sclass.name} học kỳ {semester.short_name} năm học {semester.academic_year}"
		sclass_name = unidecode.unidecode(sclass.name).lower().replace(" ", "")
		filename = f"{sclass_name}_{semester.code}_statistics.{file_format}"

	response = HttpResponse(content_type=CONTENT_TYPE_BY_FILE_FORMAT[file_format])
	response["Content-Disposition"] = f"attachment; filename={filename}"

	header = ["Mã số sinh viên", "Họ tên", "Thành tích", "Tổng điểm", "Điều 1", "Điều 2", "Điều 3", "Điều 4", "Điều 5", "Điều 6"]

	if file_format == "pdf":
		return write_statistics_data_to_pdf(response=response, header=header, students_summary_list=students_summary_list, title_text=title_text)

	return write_statistics_data_to_csv(response=response, header=header, students_summary_list=students_summary_list)


def write_statistics_data_to_csv(response=None, header=None, students_summary_list=None):
	writer = csv.writer(response)
	writer.writerow(header)
	for student_summary in students_summary_list:
		row = [
			student_summary["code"],
			student_summary["full_name"],
			student_summary["achievement"],
			student_summary["total_points"],
		]
		for training_point in student_summary["training_points"]:
			row.append(training_point["adjusted_point"])
		writer.writerow(row)

	return response


def write_statistics_data_to_pdf(response=None, header=None, students_summary_list=None, **options):
	styles = getSampleStyleSheet()
	title_style = ParagraphStyle(name="Title", parent=styles["Title"], fontName="DejaVuSans", fontSize=20, leading=24, alignment=1)
	title = Paragraph(text=options["title_text"], style=title_style)
	elements = [title, ]

	table_data = [header, ]
	for student_summary in students_summary_list:
		row = [student_summary["code"], student_summary["full_name"], student_summary["achievement"], student_summary["total_points"]]
		for training_point in student_summary["training_points"]:
			row.append(training_point["adjusted_point"])
		table_data.append(row)

	col_widths = [0] * len(table_data[0])
	for row in table_data:
		for i, cell in enumerate(row):
			cell_width = stringWidth(text=str(cell), fontName="DejaVuSans", fontSize=10) + 15
			col_widths[i] = max(col_widths[i], cell_width)
	table = Table(data=table_data, colWidths=col_widths)
	table.setStyle(TableStyle(
		[
			("BACKGROUND", (0, 0), (-1, 0), colors.grey),
			("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
			("ALIGN", (0, 0), (-1, -1), "CENTER"),
			("FONTNAME", (0, 0), (-1, -1), "DejaVuSans"),
			("FONTSIZE", (0, 0), (-1, 0), 10),
			("BOTTOMPADDING", (0, 0), (-1, 0), 12),
			("BACKGROUND", (0, 1), (-1, -1), colors.beige),
			("GRID", (0, 0), (-1, -1), 1, colors.black),
		]
	))
	elements.append(table)

	doc = SimpleDocTemplate(filename=response, pagesize=landscape(A4))
	doc.build(elements)
	return response
