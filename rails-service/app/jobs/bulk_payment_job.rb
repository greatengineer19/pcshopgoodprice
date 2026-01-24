class BulkPaymentJob < ApplicationJob
  queue_as :default

  def perform(total_payments: 0, start_time: Time.zone.now, request_uuid:)
    return if total_payments.zero?

    entry = ImportPaymentEntry.create!({
      total_payments: total_payments,
      start_time: start_time,
      request_uuid: request_uuid
    })
    processed_payments = 0

    user_ids = User.limit(10).pluck(:id)
    account_ids = Account.where(account_type: :revenue).pluck(:id)
    payment_methods = Payment.payment_methods.keys

    while processed_payments < total_payments
      ActiveRecord::Base.transaction do
        processing_payments = total_payments - processed_payments
        processing_payments = 10 if processing_payments > 10

        processing_payments.times do |i|
          revenue_id = account_ids.sample

          payment = Payment.create(
            user_id: user_ids.sample,
            debit_account_id: revenue_id,
            account_id: revenue_id,
            amount: rand(100..999),
            currency: :idr,
            payment_method: payment_methods.sample,
            request_uuid: request_uuid
          )

          JournalEntry::Creator.new(
            source: payment,
            reversed_by_id: nil
          ).call!
        end
      end

      processed_payments += 10
    end

    entry.update!(end_time: Time.zone.now)
    return "Bulk payment job completed #{processed_payments} payments"
  rescue StandardError => e
    # TODO: Create an entity called BulkPaymentRequest to capture completed / failed requests
    Rails.logger.error "Error processing bulk payment: #{e.message}"
    JournalEntry.where(reference_id: Payment.where(request_uuid: request_uuid).ids, reference_type: 'Payment').destroy_all
    Payment.where(request_uuid: request_uuid).destroy_all
    raise
  end
end
