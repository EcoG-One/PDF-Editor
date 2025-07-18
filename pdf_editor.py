import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import PyPDF2
import fitz  # PyMuPDF
from PIL import Image, ImageTk
import os
import io

class PDFEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Editor")
        self.root.geometry("1000x700")
        
        self.current_pdf = None
        self.current_doc = None
        self.current_page = 0
        self.total_pages = 0
        self.zoom_level = 1.0
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Toolbar
        toolbar = ttk.Frame(main_frame)
        toolbar.pack(fill=tk.X, pady=(0, 10))
        
        # File operations
        ttk.Button(toolbar, text="Open PDF", command=self.open_pdf).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Save PDF", command=self.save_pdf).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Export Page as Image", command=self.export_page_image).pack(side=tk.LEFT, padx=5)
        
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # PDF operations
        ttk.Button(toolbar, text="Merge PDFs", command=self.merge_pdfs).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Split PDF", command=self.split_pdf).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Extract Pages", command=self.extract_pages).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Rotate Page", command=self.rotate_page).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Add Text", command=self.add_text).pack(side=tk.LEFT, padx=5)
        
        # Content frame
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left panel for PDF preview
        left_panel = ttk.Frame(content_frame)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Navigation frame
        nav_frame = ttk.Frame(left_panel)
        nav_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(nav_frame, text="◀ Previous", command=self.prev_page).pack(side=tk.LEFT, padx=5)
        ttk.Button(nav_frame, text="Next ▶", command=self.next_page).pack(side=tk.LEFT, padx=5)
        
        self.page_label = ttk.Label(nav_frame, text="Page: 0 / 0")
        self.page_label.pack(side=tk.LEFT, padx=20)
        
        # Zoom controls
        ttk.Label(nav_frame, text="Zoom:").pack(side=tk.LEFT, padx=(20, 5))
        ttk.Button(nav_frame, text="−", command=self.zoom_out).pack(side=tk.LEFT, padx=2)
        ttk.Button(nav_frame, text="+", command=self.zoom_in).pack(side=tk.LEFT, padx=2)
        ttk.Button(nav_frame, text="Fit", command=self.fit_to_window).pack(side=tk.LEFT, padx=5)
        
        # Canvas for PDF preview
        self.canvas_frame = ttk.Frame(left_panel)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(self.canvas_frame, bg="white")
        self.h_scrollbar = ttk.Scrollbar(self.canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.v_scrollbar = ttk.Scrollbar(self.canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=self.h_scrollbar.set, yscrollcommand=self.v_scrollbar.set)
        
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Right panel for info
        right_panel = ttk.Frame(content_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        
        # PDF info
        info_frame = ttk.LabelFrame(right_panel, text="PDF Information", padding=10)
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.info_text = tk.Text(info_frame, height=10, width=30)
        self.info_text.pack(fill=tk.BOTH, expand=True)
        
        # Status bar
        self.status_bar = ttk.Label(main_frame, text="Ready", relief=tk.SUNKEN)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))
        
    def open_pdf(self):
        file_path = filedialog.askopenfilename(
            title="Select PDF file",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                self.current_pdf = file_path
                self.current_doc = fitz.open(file_path)
                self.total_pages = len(self.current_doc)
                self.current_page = 0
                
                self.update_page_display()
                self.update_pdf_info()
                self.status_bar.config(text=f"Opened: {os.path.basename(file_path)}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open PDF: {str(e)}")
                
    def update_page_display(self):
        if self.current_doc and self.current_page < self.total_pages:
            page = self.current_doc[self.current_page]
            
            # Render page as image
            mat = fitz.Matrix(self.zoom_level, self.zoom_level)
            pix = page.get_pixmap(matrix=mat)
            img_data = pix.tobytes("ppm")
            
            # Convert to PIL Image and then to PhotoImage
            img = Image.open(io.BytesIO(img_data))
            self.photo = ImageTk.PhotoImage(img)
            
            # Update canvas
            self.canvas.delete("all")
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            
            # Update page label
            self.page_label.config(text=f"Page: {self.current_page + 1} / {self.total_pages}")
            
    def update_pdf_info(self):
        if self.current_doc:
            info = self.current_doc.metadata
            info_text = f"Title: {info.get('title', 'N/A')}\n"
            info_text += f"Author: {info.get('author', 'N/A')}\n"
            info_text += f"Subject: {info.get('subject', 'N/A')}\n"
            info_text += f"Creator: {info.get('creator', 'N/A')}\n"
            info_text += f"Producer: {info.get('producer', 'N/A')}\n"
            info_text += f"Creation Date: {info.get('creationDate', 'N/A')}\n"
            info_text += f"Modification Date: {info.get('modDate', 'N/A')}\n"
            info_text += f"Total Pages: {self.total_pages}\n"
            
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(1.0, info_text)
            
    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.update_page_display()
            
    def next_page(self):
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.update_page_display()
            
    def zoom_in(self):
        self.zoom_level *= 1.2
        self.update_page_display()
        
    def zoom_out(self):
        self.zoom_level /= 1.2
        self.update_page_display()
        
    def fit_to_window(self):
        if self.current_doc:
            page = self.current_doc[self.current_page]
            page_rect = page.rect
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            if canvas_width > 1 and canvas_height > 1:
                zoom_x = canvas_width / page_rect.width
                zoom_y = canvas_height / page_rect.height
                self.zoom_level = min(zoom_x, zoom_y) * 0.9
                self.update_page_display()
                
    def save_pdf(self):
        if not self.current_doc:
            messagebox.showwarning("Warning", "No PDF loaded")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                self.current_doc.save(file_path)
                messagebox.showinfo("Success", f"PDF saved as: {file_path}")
                self.status_bar.config(text=f"Saved: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save PDF: {str(e)}")
                
    def export_page_image(self):
        if not self.current_doc:
            messagebox.showwarning("Warning", "No PDF loaded")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                page = self.current_doc[self.current_page]
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # Higher resolution
                pix.save(file_path)
                messagebox.showinfo("Success", f"Page exported as: {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export page: {str(e)}")
                
    def merge_pdfs(self):
        files = filedialog.askopenfilenames(
            title="Select PDF files to merge",
            filetypes=[("PDF files", "*.pdf")]
        )
        
        if len(files) < 2:
            messagebox.showwarning("Warning", "Please select at least 2 PDF files")
            return
            
        output_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")]
        )
        
        if output_path:
            try:
                merger = PyPDF2.PdfMerger()
                for file in files:
                    merger.append(file)
                    
                with open(output_path, 'wb') as output_file:
                    merger.write(output_file)
                    
                merger.close()
                messagebox.showinfo("Success", f"PDFs merged successfully: {output_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to merge PDFs: {str(e)}")
                
    def split_pdf(self):
        if not self.current_pdf:
            messagebox.showwarning("Warning", "No PDF loaded")
            return
            
        output_dir = filedialog.askdirectory(title="Select output directory")
        if not output_dir:
            return
            
        try:
            with open(self.current_pdf, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page_num in range(len(pdf_reader.pages)):
                    pdf_writer = PyPDF2.PdfWriter()
                    pdf_writer.add_page(pdf_reader.pages[page_num])
                    
                    output_path = os.path.join(output_dir, f"page_{page_num + 1}.pdf")
                    with open(output_path, 'wb') as output_file:
                        pdf_writer.write(output_file)
                        
            messagebox.showinfo("Success", f"PDF split into {len(pdf_reader.pages)} files")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to split PDF: {str(e)}")
            
    def extract_pages(self):
        if not self.current_pdf:
            messagebox.showwarning("Warning", "No PDF loaded")
            return
            
        # Get page range from user
        page_range = simpledialog.askstring(
            "Extract Pages",
            f"Enter page range (e.g., 1-5 or 1,3,5)\nTotal pages: {self.total_pages}:"
        )
        
        if not page_range:
            return
            
        output_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")]
        )
        
        if output_path:
            try:
                pages_to_extract = self.parse_page_range(page_range)
                
                with open(self.current_pdf, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    pdf_writer = PyPDF2.PdfWriter()
                    
                    for page_num in pages_to_extract:
                        if 1 <= page_num <= len(pdf_reader.pages):
                            pdf_writer.add_page(pdf_reader.pages[page_num - 1])
                            
                    with open(output_path, 'wb') as output_file:
                        pdf_writer.write(output_file)
                        
                messagebox.showinfo("Success", f"Pages extracted to: {output_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to extract pages: {str(e)}")
                
    def parse_page_range(self, page_range):
        pages = []
        parts = page_range.split(',')
        
        for part in parts:
            part = part.strip()
            if '-' in part:
                start, end = map(int, part.split('-'))
                pages.extend(range(start, end + 1))
            else:
                pages.append(int(part))
                
        return sorted(set(pages))
        
    def rotate_page(self):
        if not self.current_doc:
            messagebox.showwarning("Warning", "No PDF loaded")
            return
            
        angle = simpledialog.askinteger(
            "Rotate Page",
            "Enter rotation angle (90, 180, 270):",
            initialvalue=90
        )
        
        if angle in [90, 180, 270]:
            try:
                page = self.current_doc[self.current_page]
                page.set_rotation(angle)
                self.update_page_display()
                messagebox.showinfo("Success", f"Page rotated by {angle} degrees")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to rotate page: {str(e)}")
                
    def add_text(self):
        if not self.current_doc:
            messagebox.showwarning("Warning", "No PDF loaded")
            return
            
        text = simpledialog.askstring("Add Text", "Enter text to add:")
        if not text:
            return
            
        try:
            page = self.current_doc[self.current_page]
            
            # Add text at a default position
            point = fitz.Point(50, 50)
            page.insert_text(point, text, fontsize=12, color=(0, 0, 0))
            
            self.update_page_display()
            messagebox.showinfo("Success", "Text added to page")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add text: {str(e)}")


def main():
    root = tk.Tk()
    app = PDFEditor(root)
    root.mainloop()


if __name__ == "__main__":
    main()
