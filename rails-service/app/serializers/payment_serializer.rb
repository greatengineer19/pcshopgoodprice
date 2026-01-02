class PaymentSerializer < ActiveModel::Serializer
	attributes :debit_account_id, :amount, :payment_method, :currency, :created_at

	belongs_to :debit_account, class_name: 'Account'
end