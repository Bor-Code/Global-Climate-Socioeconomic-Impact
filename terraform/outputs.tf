output "instance_public_ip" {
  description = "Public IP of the EC2 instance"
  value       = aws_instance.climate_app_server.public_ip
}

output "streamlit_url" {
  description = "URL for the Streamlit Dashboard"
  value       = "http://${aws_instance.climate_app_server.public_ip}:8501"
}

output "fastapi_docs_url" {
  description = "URL for the FastAPI Swagger UI"
  value       = "http://${aws_instance.climate_app_server.public_ip}:8000/docs"
}

output "dagster_url" {
  description = "URL for the Dagster Webserver"
  value       = "http://${aws_instance.climate_app_server.public_ip}:3000"
}
