import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io
import base64
from PIL import Image
from together import Together
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DataAnalystAgent:
    """
    Core agent class that handles data analysis using Together.ai's Llama model
    """
    
    def __init__(self):
        """Initialize the Together.ai client with the Llama model"""
        # Get API key from environment variables
        self.api_key = os.getenv("TOGETHERAI_API_KEY")
        if not self.api_key:
            raise ValueError("TOGETHERAI_API_KEY not found in environment variables")
        
        # Initialize Together client
        self.client = Together(api_key=self.api_key)
        self.model = "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8"
        
    def process_query(self, query, uploaded_data, conversation_history):
        """
        Process user query and return AI response with optional visualization
        
        Args:
            query (str): User's question
            uploaded_data (dict): Dictionary of uploaded files and their data
            conversation_history (list): Previous conversation messages
            
        Returns:
            tuple: (response_text, matplotlib_figure_or_None)
        """
        try:
            # Analyze the query to determine if visualization is needed
            needs_visualization = self._needs_visualization(query)
            
            # Prepare data context for the LLM
            data_context = self._prepare_data_context(uploaded_data)
            
            # Get response from LLM
            response = self._get_llm_response(query, data_context, conversation_history)
            
            # Generate visualization if needed
            chart = None
            if needs_visualization and self._has_tabular_data(uploaded_data):
                chart = self._generate_visualization(query, uploaded_data, response)
            
            return response, chart
            
        except Exception as e:
            return f"Error processing query: {str(e)}", None
    
    def _needs_visualization(self, query):
        """Determine if the query requires a visualization"""
        viz_keywords = [
            'plot', 'chart', 'graph', 'visualize', 'show', 'display',
            'histogram', 'scatter', 'bar', 'line', 'pie', 'distribution',
            'correlation', 'trend', 'compare', 'relationship'
        ]
        return any(keyword in query.lower() for keyword in viz_keywords)
    
    def _has_tabular_data(self, uploaded_data):
        """Check if any uploaded data is tabular (DataFrame)"""
        return any(file_info['type'] == 'dataframe' for file_info in uploaded_data.values())
    
    def _prepare_data_context(self, uploaded_data):
        """Prepare a summary of uploaded data for the LLM"""
        context = "Available data:\n"
        
        for filename, file_info in uploaded_data.items():
            context += f"\n{filename}:\n"
            
            if file_info['type'] == 'dataframe':
                df = file_info['data']
                context += f"  - Type: Tabular data\n"
                context += f"  - Shape: {df.shape[0]} rows, {df.shape[1]} columns\n"
                context += f"  - Columns: {', '.join(df.columns.tolist())}\n"
                
                # Add basic statistics for numeric columns
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) > 0:
                    context += f"  - Numeric columns: {', '.join(numeric_cols)}\n"
                    for col in numeric_cols[:3]:  # Limit to first 3 columns
                        context += f"    - {col}: mean={df[col].mean():.2f}, std={df[col].std():.2f}\n"
                
                # Add sample of categorical data
                categorical_cols = df.select_dtypes(include=['object']).columns
                if len(categorical_cols) > 0:
                    context += f"  - Categorical columns: {', '.join(categorical_cols)}\n"
                    
            elif file_info['type'] == 'text':
                context += f"  - Type: Text document\n"
                context += f"  - Content preview: {file_info['data'][:200]}...\n"
                
            elif file_info['type'] == 'image':
                context += f"  - Type: Image\n"
                context += f"  - Size: {file_info['data'].size}\n"
                context += f"  - Format: {file_info['data'].format}\n"
        
        return context
    
    def _get_llm_response(self, query, data_context, conversation_history):
        """Get response from the LLM"""
        # Prepare conversation context
        messages = [
            {
                "role": "system",
                "content": """You are an expert data analyst. You help users understand and analyze their data by providing clear, actionable insights. 

When analyzing data:
1. Be specific and reference the actual data
2. Provide statistical insights when relevant
3. Suggest visualizations when appropriate
4. Explain your reasoning clearly
5. If asked to create a visualization, describe what type would be most appropriate

Available data context:
""" + data_context
            }
        ]
        
        # Add recent conversation history (last 6 messages to avoid token limit)
        recent_history = conversation_history[-6:] if len(conversation_history) > 6 else conversation_history
        for msg in recent_history:
            if msg["role"] in ["user", "assistant"]:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        # Add current query
        messages.append({
            "role": "user",
            "content": query
        })
        
        # Call Together.ai API
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=1000,
            temperature=0.7,
        )
        
        return response.choices[0].message.content
    
    def _generate_visualization(self, query, uploaded_data, llm_response):
        """Generate matplotlib visualization based on query and data"""
        try:
            # Find the first tabular dataset
            df = None
            for file_info in uploaded_data.values():
                if file_info['type'] == 'dataframe':
                    df = file_info['data']
                    break
            
            if df is None:
                return None
            
            # Create a new figure
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Determine visualization type based on query
            query_lower = query.lower()
            
            if 'histogram' in query_lower or 'distribution' in query_lower:
                # Create histogram for first numeric column
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) > 0:
                    ax.hist(df[numeric_cols[0]].dropna(), bins=20, alpha=0.7, edgecolor='black')
                    ax.set_title(f'Distribution of {numeric_cols[0]}')
                    ax.set_xlabel(numeric_cols[0])
                    ax.set_ylabel('Frequency')
                    
            elif 'scatter' in query_lower and 'plot' in query_lower:
                # Create scatter plot with first two numeric columns
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) >= 2:
                    ax.scatter(df[numeric_cols[0]], df[numeric_cols[1]], alpha=0.6)
                    ax.set_xlabel(numeric_cols[0])
                    ax.set_ylabel(numeric_cols[1])
                    ax.set_title(f'{numeric_cols[0]} vs {numeric_cols[1]}')
                    
            elif 'bar' in query_lower or 'count' in query_lower:
                # Create bar chart for categorical data
                categorical_cols = df.select_dtypes(include=['object']).columns
                if len(categorical_cols) > 0:
                    value_counts = df[categorical_cols[0]].value_counts().head(10)
                    ax.bar(range(len(value_counts)), value_counts.values)
                    ax.set_xticks(range(len(value_counts)))
                    ax.set_xticklabels(value_counts.index, rotation=45, ha='right')
                    ax.set_title(f'Count of {categorical_cols[0]}')
                    ax.set_ylabel('Count')
                    
            elif 'line' in query_lower or 'trend' in query_lower:
                # Create line plot for numeric data
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) > 0:
                    ax.plot(df.index, df[numeric_cols[0]])
                    ax.set_title(f'{numeric_cols[0]} Trend')
                    ax.set_xlabel('Index')
                    ax.set_ylabel(numeric_cols[0])
                    
            else:
                # Default: correlation heatmap if multiple numeric columns
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) >= 2:
                    correlation_matrix = df[numeric_cols].corr()
                    im = ax.imshow(correlation_matrix, cmap='coolwarm', aspect='auto')
                    ax.set_xticks(range(len(numeric_cols)))
                    ax.set_yticks(range(len(numeric_cols)))
                    ax.set_xticklabels(numeric_cols, rotation=45, ha='right')
                    ax.set_yticklabels(numeric_cols)
                    ax.set_title('Correlation Matrix')
                    
                    # Add colorbar
                    plt.colorbar(im, ax=ax)
                    
                    # Add correlation values as text
                    for i in range(len(numeric_cols)):
                        for j in range(len(numeric_cols)):
                            text = ax.text(j, i, f'{correlation_matrix.iloc[i, j]:.2f}',
                                         ha="center", va="center", color="black", fontsize=8)
                else:
                    # Simple histogram as fallback
                    if len(numeric_cols) > 0:
                        ax.hist(df[numeric_cols[0]].dropna(), bins=20, alpha=0.7, edgecolor='black')
                        ax.set_title(f'Distribution of {numeric_cols[0]}')
                        ax.set_xlabel(numeric_cols[0])
                        ax.set_ylabel('Frequency')
            
            plt.tight_layout()
            return fig
            
        except Exception as e:
            print(f"Error generating visualization: {e}")
            return None
    
    def analyze_tabular_data(self, df, query):
        """Analyze tabular data with pandas operations"""
        try:
            analysis_results = {}
            
            # Basic statistics
            analysis_results['shape'] = df.shape
            analysis_results['columns'] = df.columns.tolist()
            analysis_results['dtypes'] = df.dtypes.to_dict()
            
            # Numeric analysis
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                analysis_results['numeric_summary'] = df[numeric_cols].describe().to_dict()
                analysis_results['correlation'] = df[numeric_cols].corr().to_dict()
            
            # Categorical analysis
            categorical_cols = df.select_dtypes(include=['object']).columns
            if len(categorical_cols) > 0:
                analysis_results['categorical_counts'] = {}
                for col in categorical_cols:
                    analysis_results['categorical_counts'][col] = df[col].value_counts().head(10).to_dict()
            
            # Missing values
            analysis_results['missing_values'] = df.isnull().sum().to_dict()
            
            return analysis_results
            
        except Exception as e:
            return {"error": str(e)}
    
    def describe_image(self, image, query):
        """Describe an image using the LLM"""
        try:
            # Convert PIL image to base64 for description
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            # Create a prompt for image description
            prompt = f"""
            Please analyze this image and answer the following question: {query}
            
            Provide a detailed description of what you see in the image, including:
            - Main objects or subjects
            - Colors and composition
            - Any text or numbers visible
            - Overall context or setting
            - Anything relevant to the user's question
            """
            
            # Note: This is a simplified version. The actual Together.ai API might have
            # specific methods for image analysis. For now, we'll return a general response.
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at analyzing images and providing detailed descriptions."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7,
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Error analyzing image: {str(e)}"
    
    def analyze_text_document(self, text, query):
        """Analyze text document content"""
        try:
            # Prepare prompt for text analysis
            prompt = f"""
            Please analyze the following text document and answer this question: {query}
            
            Document content:
            {text[:2000]}...  # Truncate for token limits
            
            Provide insights, summaries, or specific information based on the user's question.
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at analyzing text documents and extracting insights."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.7,
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Error analyzing text: {str(e)}"
