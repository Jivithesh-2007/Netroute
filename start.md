# Quick Start Guide — NetRoute

### 1. Open Terminal and Navigate to Project
```bash
cd "/Users/jeslinjp/Library/CloudStorage/GoogleDrive-jeslin3379@gmail.com/My Drive/my_project/Netroute"
```

### 2. Activate the Virtual Environment
```bash
source .venv/bin/activate
```
*(Your terminal prompt will display (.venv) on the left).*

### 3. (Optional) Run the Automated Test Suite
Verify that all 56 algorithms and simulation tests pass:
```bash
python3 -m unittest discover -s tests -p "test_*.py" -v
```

### 4. Launch the Streamlit Web Application
```bash
streamlit run main.py
```

### 5. Open in Your Browser
Visit:
```
http://localhost:8501
```

---
*To stop the server at any time, press **Ctrl + C** in the terminal where Streamlit is running.*
