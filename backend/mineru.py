from gradio_client import Client, handle_file

client = Client("opendatalab/MinerU")
result = client.predict(
		file_path=handle_file('C:\\Users\\Nicole\\Desktop\\vue-project\\files\\doc1.pdf'),
		api_name="/to_pdf"
)
print(result)