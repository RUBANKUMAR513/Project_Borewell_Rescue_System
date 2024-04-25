import cv2
import numpy as np
from keras.models import load_model

def facialemotion():
    print("Inside facialemotion() function")
    # Load the pre-trained model
    model = load_model('model_file_30epochs.h5')

    # Access the video stream
    video = cv2.VideoCapture('http://192.168.4.1:81/stream')

    # Load the cascade classifier for face detection
    faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

    # Dictionary for mapping emotion labels to strings
    labels_dict = {0: 'Angry', 1: 'Disgust', 2: 'Fear', 3: 'Happy', 4: 'Neutral', 5: 'Sad', 6: 'Surprise'}

    while True:
        # Read a frame from the video stream
        ret, frame = video.read()
        if not ret:
            break

        # Convert the frame to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect faces in the grayscale frame
        faces = faceCascade.detectMultiScale(gray, 1.3, 3)

        # Process each detected face
        for (x, y, w, h) in faces:
            # Extract the face region
            sub_face_img = gray[y:y+h, x:x+w]
            # Resize the face image to match model input size
            resized = cv2.resize(sub_face_img, (48, 48))
            # Normalize the resized image
            normalized = resized / 255.0
            # Reshape the image for model input
            reshaped = np.reshape(normalized, (1, 48, 48, 1))
            # Predict emotion using the loaded model
            result = model.predict(reshaped)
            label = np.argmax(result, axis=1)[0]

            # Draw bounding box around the face
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 1)
            # Draw filled rectangle as background for emotion label
            cv2.rectangle(frame, (x, y-40), (x+w, y), (50, 50, 255), -1)
            # Put text (emotion label) on the frame
            cv2.putText(frame, labels_dict[label], (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        # Convert the frame to JPEG format
        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        # Yield the frame bytes
        yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    # Release video capture
    video.release()
    cv2.destroyAllWindows()
