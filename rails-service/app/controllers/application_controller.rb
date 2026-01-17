class ApplicationController < ActionController::Base
  rescue_from StandardError, NameError, with: :handle_standard_error
  rescue_from ActiveRecord::RecordNotFound, with: :handle_record_not_found
  rescue_from ActiveRecord::RecordInvalid, with: :handle_record_invalid
  rescue_from ActionView::Template::Error, with: :handle_template_error

  private

    def handle_standard_error(exception)
      render json: { message: exception.message }, status: :internal_server_error
    end

    def handle_record_not_found(exception)
      render json: { status: I18n.t('general_errors.record_not_found'), message: exception.message }, status: :not_found
    end

    def handle_record_invalid(exception)
      render json: { status: I18n.t('general_errors.record_invalid'), message: exception.message }, status: :unprocessable_entity
    end

    def handle_template_error(exception)
      render json: { message: exception.message }, status: :internal_server_error
    end
end
