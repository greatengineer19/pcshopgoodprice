class User < ApplicationRecord
  has_secure_password

  has_many :accounts

  after_validation :copy_password_digest

  def copy_password_digest
    self.hashed_password = password_digest
  end
end
