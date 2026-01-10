class UserSerializer < ActiveModel::Serializer
	attributes :id, :role, :fullname, :created_at
end