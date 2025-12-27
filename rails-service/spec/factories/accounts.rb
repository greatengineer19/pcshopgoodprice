FactoryBot.define do
	factory :account do
    is_active { true }
    subtype { 0 } # Always 0 first
  end
end