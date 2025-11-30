from fpdf import FPDF

def create_pdf(quiz_data, topic, difficulty):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt=f"Quiz: {topic} ({difficulty})", ln=True, align="C")
    pdf.ln(5)

    for i, q in enumerate(quiz_data, start=1):
        pdf.multi_cell(0, 8, txt=f"{i}. {q['question']}")
        for opt in q["options"]:
            pdf.multi_cell(0, 8, txt=f"    - {opt}")
        pdf.ln(3)

    file_path = "quiz.pdf"
    pdf.output(file_path)

    return file_path
