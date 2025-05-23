# Use a lightweight Python base image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all your app code
COPY . .

# Expose the port Streamlit will run on
EXPOSE 8501

# Run your app via Python (not Streamlit CLI) to avoid Railway port issues
CMD ["python", "launch"]





