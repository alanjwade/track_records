from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from reportlab.lib.utils import simpleSplit


class PDFReport:
    def __init__(self, filename):
        self.filename = filename
        self.canvas = canvas.Canvas(filename, pagesize=letter)
        self.width, self.height = letter

    def create_pdf(self, track_records):
        self.canvas.setFont("Helvetica", 12)
        # self.canvas.drawString(100, self.height - 40, "Track Records Report")

        def parse_results(results):
            '''Given a list of results, group them by athlete.'''
            athlete_results = {}
            for result in results:
                athlete_name = result["athlete_name"]
                if athlete_name not in athlete_results:
                    athlete_results[athlete_name] = []
                athlete_results[athlete_name].append(result)

            return athlete_results

        def add_page(self):
            self.canvas.showPage()
            self.canvas.setFont("Helvetica", 12)
            self.width, self.height = letter

        def make_one_table(self, athlete_name, records):
            '''Make a table for one athlete.'''

            title_height = self.height - 40
            name_height = self.height - 60
            table_page_height = self.height - 120
            self.canvas.setFont("Helvetica-Bold", 20)
            self.canvas.drawString(100, title_height, "St. Joseph Track Goals")
            self.canvas.drawString(100, name_height, athlete_name)
            self.canvas.setFont("Helvetica", 12)
            self.canvas.drawString(100, table_page_height + 20, "Current Personal Records")
            table_data = [["Event", "Result", "Date", "Location"]]
            for record in records:
                table_data.append([
                    record["event_name"],
                    record["result"],
                    record["meet_date"],
                    record["location"]])
            table = Table(table_data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            table_width, table_height = table.wrapOn(self.canvas, self.width, self.height)
            table.drawOn(self.canvas, 100, table_page_height - table_height)
            self.canvas.saveState()
            watermark_image = ImageReader('data/stj-logo-final-wh-mobile.png')
            self.canvas.saveState()
            self.canvas.setFillAlpha(0.1)
            img_width, img_height = watermark_image.getSize()
            aspect_ratio = img_width / img_height
            new_width = self.width - 200
            new_height = new_width / aspect_ratio
            if new_height > self.height - 200:
                new_height = self.height - 200
                new_width = new_height * aspect_ratio
            x_position = (self.width - new_width) / 2
            y_position = (self.height - new_height) / 2
            self.canvas.drawImage(watermark_image, x_position, y_position, width=new_width, height=new_height, mask='auto')
            self.canvas.restoreState()
            # self.canvas.drawTable(table_data, x=100, y=self.height - 80)
        
        def add_paragraph(self):
            '''Add a motivational paragraph and goal lines with text wrapping.'''
            paragraph_text = (
            "Set goals for this season. The goals can be certain times/distances, "
            "places, or something less concrete (Have fun at practice! Try 6 events!)."
            )
            goal_line_texts = [
            "Goal 1: ",
            "Goal 2: ",
            "Goal 3: "
            ]
            self.canvas.setFont("Helvetica", 12)
            middle_of_page = self.height / 2

            # Wrap the paragraph text
            wrapped_text = simpleSplit(paragraph_text, "Helvetica", 12, self.width - 200)

            # Draw the wrapped text
            y_position = middle_of_page + 50
            for line in wrapped_text:
                self.canvas.drawString(100, y_position, line)
                y_position -= 15  # Adjust line spacing

            # Draw the goal lines
            for goal_line_text in goal_line_texts:
                self.canvas.drawString(100, y_position - 30, goal_line_text)
                self.canvas.line(200, y_position - 30, self.width - 100, y_position - 30)
                y_position -= 40  # Adjust spacing between goal lines

        for athlete_record in parse_results(track_records).items():
            athlete_name, records = athlete_record

            make_one_table(self, athlete_name, records)


            add_paragraph(self)

            if athlete_record != list(parse_results(track_records).items())[-1]:
                add_page(self)



        self.canvas.save()


        
        PDFReport.add_page = add_page
# Example usage:
# track_records = [
#     {"id": 1, "name": "Track 1", "time": "3:45"},
#     {"id": 2, "name": "Track 2", "time": "4:20"},
#     # Add more records as needed
# ]
# report = PDFReport("track_records_report.pdf")
# report.create_pdf(track_records)


    def create_results_pdf(self, results):
        """Create a PDF with results organized by athlete/event with dates as columns."""
        # Filter for results from 2024 or later
        results = [r for r in results if r['meet_date'].split('-')[0] >= '2024']
        
        # Extract all unique dates
        dates = sorted(list({result['meet_date'] for result in results}))
        
        # Group results by athlete and event
        athlete_event_results = {}
        for result in results:
            key = (result['athlete_name'], result['event_name'])
            if key not in athlete_event_results:
                athlete_event_results[key] = {}
            athlete_event_results[key][result['meet_date']] = {
                'result': result['result'],
                'result_sort': result['result_sort']
            }

        # Create table data and best results marker
        table_data = [['Athlete', 'Event'] + [date.split()[0] for date in dates]]  # Use first word of date only
        is_best_result = [[False] * len(table_data[0])]  # First row (headers) all False
        
        for (athlete, event), date_results in sorted(athlete_event_results.items()):
            row = [athlete, event]
            row_best = [False, False]  # First two columns (athlete, event) always False
            best_result_sort = min([date_results[d]['result_sort'] for d in date_results.keys() if date_results[d]['result_sort'] is not None], default=None)
            
            for date in dates:
                result = date_results.get(date, {'result': '', 'result_sort': None})
                is_best = result['result_sort'] == best_result_sort and result['result_sort'] is not None
                row.append(result['result'])
                row_best.append(is_best)
            
            table_data.append(row)
            is_best_result.append(row_best)


        # Style configuration
        col_widths = [120, 80] + [40] * len(dates)  # Fixed widths for columns
        table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),  # Smaller font size
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ])

        # Split data into pages
        rows_per_page = 30  # Adjust this value based on your needs
        for i in range(0, len(table_data), rows_per_page):
            page_data = [table_data[0]]  # Add header row to each page
            page_is_best = [is_best_result[0]]  # Add header row best results
            page_data.extend(table_data[i+1:i+rows_per_page])
            page_is_best.extend(is_best_result[i+1:i+rows_per_page])
            
            table = Table(page_data, colWidths=col_widths)
            table.setStyle(table_style)

            # Add bold style for best results
            for row_idx, row_best in enumerate(page_is_best):
                for col_idx, is_best in enumerate(row_best):
                    if is_best:
                        table.setStyle(TableStyle([
                            ('FONTNAME', (col_idx, row_idx), (col_idx, row_idx), 'Helvetica-Bold')
                        ]))

            # Draw the table for this page
            self.canvas.setFont("Helvetica-Bold", 20)
            self.canvas.drawString(100, self.height - 40, "Season Results")
            self.canvas.setFont("Helvetica", 12)
            table_width, table_height = table.wrapOn(self.canvas, self.width - 100, self.height)
            table.drawOn(self.canvas, 50, self.height - 100 - table_height)

            # Add a new page if there's more data
            if i + rows_per_page < len(table_data):
                self.canvas.showPage()

        self.canvas.save()
