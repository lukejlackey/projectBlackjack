from application import app
import application.controllers

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
 