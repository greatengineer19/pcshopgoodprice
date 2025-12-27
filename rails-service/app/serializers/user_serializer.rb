class UserSerializer < ActiveModel::Serializer
    attributes :id, :email, :name, :created_at

    has_many :accounts
end