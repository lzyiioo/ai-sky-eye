# Feature Documentation

## 📊 Feature Overview (22 Core Modules)

### 1️⃣ Basic Framework Modules

#### Safety Control System `safety_config.py`
| Feature | Description |
|---------|-------------|
| Three Levels | strict / normal / off |
| Sensitive Areas | Screen edges, system menu protection |
| Rate Limiting | Prevent operations too fast |
| Audit Log | Record all operations |

**Core API:**
```python
from screen_controller.safety_config import SafetyConfig
config = SafetyConfig(level="normal")
```

---

#### Multi-Backend Screenshot `enhanced_screenshot.py`
| Backend | Characteristics | Priority |
|---------|-----------------|----------|
| dxcam | GPU acceleration, highest performance | 1 |
| mss | Cross-platform, medium performance | 2 |
| pillow | Pure Python, most compatible | 3 |

**Core API:**
```python
from screen_controller.enhanced_screenshot import capture_screen
img = capture_screen()
```

---

### 2️⃣ UI Automation Modules

#### UI Element Finder `ui_element_finder.py`
| Feature | Description |
|---------|-------------|
| Name Search | Fuzzy text matching |
| Type Search | Button, Edit, Menu, etc. |
| Coordinate Get | Auto-calculate element center |
| Cache Optimization | Speed up repeated queries within 1 second |

**Core API:**
```python
from screen_controller.ui_element_finder import find_element, find_button
elem = find_element("OK")
button = find_button("Login")
```

---

#### Smart Controller `smart_controller_v2.py`
| Feature | Description |
|---------|-------------|
| ai_click | Click by name, auto-find coordinates |
| ai_type | Type by name, auto-find input field |
| ai_menu | Smart menu selection |
| wait_for_element | Wait for element to appear |

**Core API:**
```python
from screen_controller.smart_controller_v2 import ai_click, ai_type
ai_click("OK")
ai_type("Username", "admin")
```

---

### 3️⃣ AI Enhancement Modules

#### Smart Wait `ai_enhancements.py`
| Wait Type | Description |
|-----------|-------------|
| wait_for_element | Wait for element appear/disappear |
| wait_for_text | Wait for text to appear (OCR) |
| wait_for_stable | Wait for screen to stabilize |
| wait_for_change | Wait for screen to change |
| wait_for_custom | Custom condition wait |

---

#### Exception Recovery `ai_enhancements.py`
| Feature | Description |
|---------|-------------|
| Auto Retry | Retry on failure |
| Exponential Backoff | 1s, 2s, 4s, 8s... |
| Recovery Actions | Execute recovery on failure |
| Rollback | Support operation rollback |

---

#### Action Chain `ai_enhancements.py`
| Feature | Description |
|---------|-------------|
| Sequential Execution | Multi-step automation |
| Conditional Branch | if/else support |
| Variable Passing | Pass values between steps |
| Retry Mechanism | Single step retry |

---

#### Enhanced OCR `enhanced_ocr.py`
| Engine | Language | Characteristics |
|--------|----------|-----------------|
| PaddleOCR | Chinese best | High accuracy |
| EasyOCR | Multi-language | Easy to use |
| Tesseract | Basic | Lightweight |

**Supported Languages:** Chinese, English, Japanese, Korean, French, German, Spanish

---

#### Image Compare `image_compare.py`
| Feature | Description |
|---------|-------------|
| Similarity Calculation | SSIM/MSE/Pixel comparison |
| Change Region | Locate changed positions |
| Difference Visualization | Red box highlight differences |
| Continuous Monitoring | watch() real-time monitoring |

---

### 4️⃣ System Control Modules

#### Clipboard Manager `clipboard_manager.py`
- Read clipboard text
- Set clipboard content
- Image support (in development)

---

#### Window Manager `window_manager.py`
| Feature | Description |
|---------|-------------|
| list_windows | List all windows |
| find_window | Find by title |
| focus_window | Activate window |
| minimize/maximize | Minimize/Maximize |
| move_window | Move and resize |

---

#### Action Recorder `action_recorder.py`
|