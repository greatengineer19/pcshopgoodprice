module Rails
	module Api
		class PaymentsController < ApplicationController
			skip_before_action :verify_authenticity_token
		    skip_forgery_protection

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

			def bulk_create
				total_payments = (bulk_payment_params[:total_payments].presence || 10).to_i
				total_payments = 50 if total_payments > 50

				BulkPaymentJob.perform_later(total_payments: total_payments, request_uuid: bulk_payment_params[:request_uuid])

				render json: { message: "Bulk payment job started" }, status: :accepted
			end

			private

			def pagination
				params[:page] || 0
			end

			def create_params
				params.permit(
					:user_id,
					:request_uuid,
					:debit_account_id,
					:account_id,
					:amount,
					:currency,
					:payment_method
				)
			end

			def bulk_payment_params
				params.permit(:total_payments, :request_uuid)
			end
		end
	end
end
