FROM python:3.10-slim

# Install system dependencies (⬅️ this is the fix)
RUN apt-get update && apt-get install -y libgl1-mesa-glx libglib2.0-0

# Set working directory
WORKDIR /app

# Copy backend files
COPY backend /app/backend
COPY weights /app/weights
COPY requirements.txt /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port (very important for Render!)
ENV PORT 8000
EXPOSE 8000

# Set entrypoint
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
