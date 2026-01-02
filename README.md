# RapidAD AI: Unified Ad Studio (Flask Edition)

RapidAD AI is a professional, high-performance web application designed for creating high-fidelity product ads. It unifies professional image editing, AI generation, and cinematic video production into a single, sleek interface.

## 🚀 Key Features

- **🎨 Image Hub**: Generate HD product images using Bria AI with integrated Gemini-powered prompt enhancement.
- **📸 Product Studio**:
  - **Remove Background**: Clean, professional background removal.
  - **Add Shadow**: Realistic natural or drop shadows with adjustable intensity.
  - **Packshot Creator**: Transform raw product shots into studio-ready packshots.
- **🌅 Lifestyle Lab**: Create professional studio photoshoots by placing your product into custom or template-based scenes.
- **🎥 Video Ads (Veo 3.1)**: Generate cinematic video ads using Google's state-of-the-art **Veo 3.1** model.
- **✍️ Ad Creator**: Add professional Call-to-Action (CTA) text overlays with headlines and subheadlines to finalize your creatives.

## 🛠️ Technology Stack

- **Backend**: Python Flask
- **AI Models**: 
  - **Bria AI**: HD Image Generation, Background Removal, Shadows, Packshots.
  - **Google Gemini**: Prompt analysis and merging.
  - **Google Veo 3.1**: Image-to-Video generation.
- **Frontend**: HTML5, Vanilla CSS (Premium Dark Mode), JavaScript (Async API handling).

## 📂 Project Structure

- `app.py`: Main Flask application handling all API routes and logic.
- `services/`: Specialized service modules for Bria, Gemini, and Veo.
- `utils/`: Image processing and text overlay utilities.
- `templates/`: Modern, tabbed frontend interface.
- `static/`: Styling, assets, and generated uploads.

## 🚦 Getting Started

### Prerequisites

- Python 3.11+
- Bria AI API Key
- Google Cloud API Key (with Gemini and Veo access)

### Installation

1. Clone or download this directory.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up your `.env` file with your API keys:
   ```env
   BRIA_API_KEY=your_bria_key
   GOOGLE_API_KEY=your_google_key
   ```

### Running the App

Execute the following command in the project root:
```bash
python app.py
```
Open your browser and navigate to `http://localhost:5000`.

## 🎨 UI/UX Design

The application features a premium dark-mode interface inspired by modern SaaS products, utilizing:
- **Glassmorphism**: Translucent, blurred cards for a modern feel.
- **Subtle Micro-animations**: Smooth transitions between tabs and loading states.
- **Responsive Layout**: Sidebar-driven navigation with persistent feedback loops.

---
Built with ❤️ for professional ad creators.
