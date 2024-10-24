# Senorita10

# Fruit and Vegetable Shelf Life Estimator

An AI-powered freshness analysis system utilizing the Llama 3.2 VL vision model to estimate shelf life and provide storage recommendations for fruits and vegetables.

## Features

- Real-time shelf life estimation based on image analysis
- Comprehensive storage recommendations including temperature and humidity conditions
- Refrigeration guidance and custom storage tips
- History tracking of analyzed produce
- User-friendly interface with image preview

## Technologies Used

- Frontend: Streamlit, HTML
- Backend: Python, Regex
- Cloud Infrastructure: Google Cloud Platform (GCP), Vertex AI
- Vision Model: Llama 3.2 VL
- Image Processing: Pillow (PIL)
- Data Management: Pandas
- Version Control: Git, GitHub

## Installation & Setup

1. Clone this repository
```bash
git clone https://github.com/yourusername/shelf-life-estimator.git
cd shelf-life-estimator
```

2. Create a virtual environment and activate it
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Configure GCP Credentials
- Create a service account in Google Cloud Console
- Download the JSON key file
- Set up environment variables:
  ```bash
  export GOOGLE_APPLICATION_CREDENTIALS="path/to/your/service-account-key.json"
  export GOOGLE_CLOUD_PROJECT="your-project-id"
  ```

## Usage

1. Start the application:
```bash
streamlit run app.py
```

2. Open the provided URL in your web browser
3. Upload an image of a fruit or vegetable
4. Click "Estimate Shelf Life" to analyze
5. View detailed storage recommendations and history

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
