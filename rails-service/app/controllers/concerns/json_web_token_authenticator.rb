module JsonWebTokenAuthenticator
  extend ActiveSupport::Concern

  included do
    before_action :authenticate_request
    attr_reader :current_user
  end

  private

  def authenticate_request
    token = extract_token
    return render_unauthorized('Token missing') unless token

    decoded_token = JsonWebToken.decode(token)
    @current_user = User.find(decoded_token[:user_id])
  rescue ActiveRecord::RecordNotFound
    render_unauthorized('User not found')
  rescue JsonWebToken::TokenExpiredError => e
    render_unauthorized(e.message)
  rescue JsonWebToken::TokenInvalidError => e
    render_unauthorized(e.message)
  end

  def extract_token
    header = request.headers['Authorization']
    header&.split(' ')&.last if header&.start_with?('Bearer ')
  end

  def render_unauthorized(message = 'Unauthorized')
    render json: { error: message }, status: :unauthorized
  end
end