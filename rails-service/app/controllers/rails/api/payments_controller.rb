module Rails
	module Api
		class PaymentsController < ApplicationController
			def index
				@payments = Payment.all.limit(50).offset(pagination)
				render json: @payments, each_serializer: PaymentSerializer
			end

			def create
				payment = Payment.new(create_params)

				ActiveRecord::Base.transaction do
					payment.save!

					JournalEntry::Creator.new(
						source: payment,
						reversed_by_id: nil
					).call!
				end

				render json: { payment: payment }, status: :ok
			end

			private

			def pagination
				params[:page] || 0
			end

			def create_params
				params.require(
					:user_id,
					:debit_account_id,
					:amount,
					:currency,
					:payment_method,
					:description
				)
			end
		end
	end
end
