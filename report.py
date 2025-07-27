import matplotlib.pyplot as plt
from fpdf import FPDF
import os

class PDFReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Multi-Armed Bandit Algorithms Analysis', 0, 1, 'C')
    
    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(4)
    
    def chapter_body(self, body):
        self.set_font('Arial', '', 12)
        self.multi_cell(0, 10, body)
        self.ln()
    
    def add_image(self, image_path, caption):
        self.image(image_path, x=10, w=180)
        self.set_font('Arial', 'I', 10)
        self.cell(0, 10, caption, 0, 1, 'C')
        self.ln()

def generate_report():
    report = PDFReport()
    report.add_page()
    
    # Algorithm descriptions
    algorithms = {
        "Epsilon-Greedy": "Explores randomly with probability ε, exploits best arm otherwise.",
        "UCB1": "Uses confidence bounds to balance exploration and exploitation.",
        "Thompson Sampling": "Bayesian approach sampling from posterior distributions.",
        "Exp3": "Designed for adversarial bandits using exponential weights.",
        "LinUCB": "Contextual bandit algorithm using linear models and confidence bounds."
    }
    
    report.chapter_title("Algorithm Descriptions")
    for name, desc in algorithms.items():
        report.chapter_body(f"- {name}: {desc}")
    
    # Implementation details
    report.add_page()
    report.chapter_title("Implementation Details")
    report.chapter_body("Algorithms implemented from scratch in Python without external libraries.")
    
    # Add result images
    report.add_page()
    report.chapter_title("Experimental Results - Bernoulli Environment")
    report.add_image('Bernoulli_results.png', 'Cumulative Regret and Best Arm Frequency')
    
    report.add_page()
    report.chapter_title("Experimental Results - Gaussian Environment")
    report.add_image('Gaussian_results.png', 'Cumulative Regret and Best Arm Frequency')
    
    report.add_page()
    report.chapter_title("Experimental Results - Contextual Environment")
    report.add_image('Contextual_results.png', 'Cumulative Regret and Best Arm Frequency')
    
    # Summary table
    report.add_page()
    report.chapter_title("Summary Table")
    report.chapter_body("Comparative analysis of algorithm performance:")
    # Placeholder for table - in practice, use cell() methods to create a table
    report.chapter_body("[Insert summary table here]")
    
    report.output('report.pdf')

if __name__ == "__main__":
    generate_report()