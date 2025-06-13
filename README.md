# 📊 Data Analyst Agent

A comprehensive Streamlit-based application that uses Together.ai's Llama-4-Maverick-17B-128E-Instruct-FP8 model to analyze multiple file types and provide AI-powered insights through an interactive chat interface.

## 🏗️ Project Structure

```
data-analyst-agent/
├── app/                    # Streamlit application files
│   └── streamlit_app.py   # Main Streamlit interface
├── core/                  # Core agent logic
│   └── agent.py          # DataAnalystAgent class with Together.ai integration
├── utils/                 # File parsing utilities
│   └── parsers.py        # File parsers (CSV, Excel, PDF, DOCX, images)
├── tests/                 # Test files and examples
│   ├── test_agent.py     # Unit tests for the agent
│   ├── sample.csv        # Sample CSV data
│   ├── sample.pdf        # Sample PDF document
│   └── sample.jpg        # Sample image
├── .streamlit/
│   └── config.toml       # Streamlit configuration
├── .env.example          # Environment variables template
├── local_requirements.txt # Python dependencies for local installation
├── pyproject.toml        # Project configuration (for Replit)
└── README.md             # This file
```

## ✨ Features

- **Multi-format File Support**: Upload and analyze CSV, Excel, PDF, DOCX, and image files
- **AI-Powered Analysis**: Uses Together.ai's Llama-4-Maverick model for intelligent data insights
- **Interactive Chat Interface**: Ask questions about your data in natural language
- **Automatic Visualizations**: Generates matplotlib charts based on your queries
- **Real-time Processing**: Instant file parsing and caching for efficient analysis
- **Clean UI**: Modern Streamlit interface with sidebar file management

## 🚀 Quick Start (Local Installation)

### Prerequisites
- Python 3.8 or higher
- Together.ai API key (get one at: https://api.together.xyz/)

### Step-by-Step Setup

1. **Clone or download the project:**
   ```bash
   git clone <your-repo-url>
   cd data-analyst-agent
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r local_requirements.txt
   ```

4. **Set up your API key:**
   ```bash
   cp .env.example .env
   ```
   
   Then edit `.env` and add your Together.ai API key:
   ```
   TOGETHERAI_API_KEY=442bbd72dcf120871851485a63ba10d6942243524d837csskjnsd332iow
   ```
   ⚠️ **Important**: Replace the example key above with your actual API key from Together.ai

5. **Run the application:**
   ```bash
   streamlit run app/streamlit_app.py
   ```

6. **Open your browser:**
   The app will open automatically at `http://localhost:8501`

## 🔧 Usage Guide

### Uploading Files
1. Use the sidebar file uploader to select your data files
2. Supported formats: CSV, Excel (.xlsx, .xls), PDF, DOCX, and images (JPG, PNG, etc.)
3. Files are automatically processed and cached for analysis

### Asking Questions
- Type questions in the chat interface about your uploaded data
- Examples:
  - "What is the average sales by region?"
  - "Show me a histogram of the profit column"
  - "Create a scatter plot comparing sales and profit"
  - "Summarize the key insights from this data"

### Visualizations
The agent automatically generates charts when you ask for:
- Histograms: "show distribution", "create histogram"
- Scatter plots: "scatter plot", "relationship between"
- Bar charts: "bar chart", "count by category"
- Line plots: "trend over time", "line chart"
- Correlation matrices: "correlation", "relationships"

## 🧪 Testing

### Run Unit Tests
```bash
python tests/test_agent.py
```

### Test with Sample Data
The `tests/` folder contains sample files you can use to test the application:
- `sample.csv`: Sales data with multiple categories and regions
- `sample.pdf`: Business report with financial information
- `sample.jpg`: Sample image for testing image analysis

## 📝 Configuration

### Environment Variables
Create a `.env` file with the following:
```
# Together.ai API Key (REQUIRED)
TOGETHERAI_API_KEY=your_actual_api_key_here

# Optional settings
DEBUG=False
LOG_LEVEL=INFO
```

### Streamlit Configuration
The app uses the following Streamlit configuration (`.streamlit/config.toml`):
```toml
[server]
headless = true
address = "0.0.0.0"
port = 5000

[theme]
base = "light"
```

## 🔍 Architecture

### Core Components

1. **DataAnalystAgent** (`core/agent.py`):
   - Initializes Together.ai client with Llama-4-Maverick model
   - Processes user queries and generates responses
   - Creates visualizations based on query context
   - Handles different data types (tabular, text, images)

2. **File Parsers** (`utils/parsers.py`):
   - `parse_csv()`: Handles CSV files with multiple encodings
   - `parse_excel()`: Processes Excel files using openpyxl
   - `parse_pdf()`: Extracts text from PDF documents
   - `parse_docx()`: Parses Word documents
   - `parse_image()`: Loads and processes images

3. **Streamlit Interface** (`app/streamlit_app.py`):
   - File upload and management
   - Chat interface with message history
   - Real-time visualization display
   - Session state management

### Data Flow
1. User uploads file → Parser processes → Data cached in session
2. User asks question → Agent analyzes query → LLM generates response
3. If visualization needed → Matplotlib chart created → Displayed in interface

## 🛠️ Troubleshooting

### Common Issues

**"together not installed" error:**
- Make sure you install `together` (not `togetherai`)
- Run: `pip install together`

**API Key errors:**
- Verify your `.env` file exists and contains the correct API key
- Ensure the key starts with your actual Together.ai API key
- Check that python-dotenv is installed: `pip install python-dotenv`

**File parsing errors:**
- Ensure uploaded files are not corrupted
- Check file permissions and encoding
- For Excel files, make sure openpyxl is installed

**Visualization issues:**
- Verify matplotlib is properly installed
- Ensure your data has numeric columns for charts
- Check that the query contains visualization keywords

### Getting Help
- Check the console output for detailed error messages
- Review the test files for usage examples
- Ensure all dependencies are installed correctly

## 📦 Dependencies

### Required Packages
- `streamlit`: Web application framework
- `together`: Together.ai API client
- `pandas`: Data manipulation and analysis
- `numpy`: Numerical computing
- `matplotlib`: Plotting and visualization
- `python-docx`: Word document processing
- `PyPDF2`: PDF text extraction
- `pillow`: Image processing
- `openpyxl`: Excel file handling
- `python-dotenv`: Environment variable management

## 🔄 Development

### Adding New File Types
1. Create a new parser function in `utils/parsers.py`
2. Add the file extension to the uploader in `app/streamlit_app.py`
3. Update the processing logic in the `process_uploaded_file()` function

### Extending Analysis Capabilities
1. Add new methods to the `DataAnalystAgent` class
2. Update the query processing logic to handle new analysis types
3. Add corresponding visualization functions if needed

## 📊 Example Queries

### Data Analysis
- "What are the summary statistics for this dataset?"
- "Which region has the highest sales?"
- "What is the correlation between sales and profit?"
- "Show me the top 10 products by revenue"

### Visualizations
- "Create a bar chart of sales by category"
- "Show the distribution of profits"
- "Plot sales trends over time"
- "Generate a correlation heatmap"

### Document Analysis
- "Summarize the key points in this PDF"
- "What are the main findings in this report?"
- "Extract the financial data from this document"

### Image Analysis
- "Describe what you see in this image"
- "What text is visible in this picture?"
- "Analyze the charts or graphs in this image"

---

🤖 **Powered by Together.ai's Llama-4-Maverick-17B-128E-Instruct-FP8**

