from fvgvisionai.web_controller.app_service import execute_fvgvision_ai
from fvgvisionai.web_controller.web_controller import app

if __name__ == "__main__":
    execute_fvgvision_ai()
    app.run(host='0.0.0.0', port=8081)
