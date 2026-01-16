# This file should ensure the existence of records required to run the application in every environment (production,
# development, test). The code here should be idempotent so that it can be executed at any point in every environment.
# The data can then be loaded with the bin/rails db:seed command (or created alongside the database with db:setup).
#
# Example:
#
#   ["Action", "Comedy", "Drama", "Horror"].each do |genre_name|
#     MovieGenre.find_or_create_by!(name: genre_name)
#   end

Account.find_or_create_by!(
	account_code: "4010",
	account_name: "Sales Revenue",
	account_type: :revenue,
	is_active: true,
	normal_balance: :credit,
	subtype: 0
)

Account.find_or_create_by!(
	account_code: "1010",
	account_name: "Cash on Hand",
	account_type: :asset,
	is_active: true,
	normal_balance: :debit,
	subtype: 0
)

Account.find_or_create_by!(
	account_code: "1030",
	account_name: "Bank BCA Account",
	account_type: :asset,
	is_active: true,
	normal_balance: :debit,
	subtype: 0
)

Account.find_or_create_by!(
	account_code: "1031",
	account_name: "Bank BNI Account",
	account_type: :asset,
	is_active: true,
	normal_balance: :debit,
	subtype: 0
)
