from gradio_client import Client, handle_file,file

# Create the client for your hosted Gradio interface
client = Client("http://172.83.15.166:8080/")

# Define the input parameters
person_image_path = '/home/ubuntu/VTO/ZenVton/vto-production/media/bodyimage/man-rnhs-0069.jpg'
cloth_image_path = '/home/ubuntu/VTO/ZenVton/vto-production/media/cloth/cricket.png'

result = client.predict(
    param_0={
        "background": file(person_image_path),  # Provide the background image
        "layers": [file(person_image_path)],    # Provide the layers image
        "composite": file(person_image_path)    # Provide the composite image
    },
    param_1=file(cloth_image_path),  # Provide the condition image (cloth)
    param_2="upper",
		param_3=50,
		param_4=2.5,
		param_5=42,
		param_6="input & mask & result",
		api_name="/lambda"
)

print(result)
