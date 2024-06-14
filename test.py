from gradio_client import Client, handle_file

def OOt():
    client = Client("levihsu/OOTDiffusion")
    result = client.predict(
            vton_img=handle_file('/home/ubuntu/vto-production/media/Production/61349134390/full_body/WhatsApp_Image_2024-02-18_at_03.34.23_480494c9_70urmre.jpg'),
            garm_img=handle_file('https://cdn.shopify.com/s/files/1/0613/4913/4390/files/Muselot-Old-school-is-cool-printed-t-shirts-in-golden-yellow-color.webp'),
            n_samples=1,
            n_steps=20,
            image_scale=2,
            seed=-1,
            api_name="/process_hd"
    )
    print(result)
    
OOt()
    