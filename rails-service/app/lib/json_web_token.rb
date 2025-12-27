class JsonWebToken
  SECRET_KEY = Rails.application.credentials.secret_key_base || ENV['SECRET_KEY_BASE']

  # Encode a payload into a JWT token
  def self.encode(payload, exp = 24.hours.from_now)
    payload[:exp] = exp.to_i
    JWT.encode(payload, SECRET_KEY, 'HS256')
  end

  # Decode and validate a JWT token
  def self.decode(token)
    decoded, _header = JWT.decode(token, SECRET_KEY, true, algorithm: 'HS256')
    HashWithIndifferentAccess.new(decoded)
  rescue JWT::ExpiredSignature
    raise TokenExpiredError, "Token has expired"
  rescue JWT::DecodeError => e
    raise TokenInvalidError, "Invalid token: #{e.message}"
  rescue => e
    raise TokenInvalidError, "Token validation failed: #{e.message}"
  end

  class TokenExpiredError < StandardError; end
  class TokenInvalidError < StandardError; end
end