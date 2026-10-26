import pymupdf

# Create a new, blank PDF document
pdf = pymupdf.open()

# Add one blank page
pdf.new_page()

# Save the PDF in the project folder
pdf.save("empty_resume.pdf")

# Close the document
pdf.close()

print("Empty PDF created successfully!")