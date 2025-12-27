class ErrorsController < ApplicationController
  skip_before_action :verify_authenticity_token
  skip_forgery_protection
  
  def not_found
    render json: { error: "Not Found", message: "The requested resource could not be found" }, status: :not_found
  end

  def unprocessable_entity
    render json: { error: "Unprocessable Entity", message: "The request could not be processed" }, status: :unprocessable_entity
  end
  
  def internal_server_error
    render json: { error: "Internal Server Error", message: "An unexpected error occurred" }, status: :internal_server_error
  end
end