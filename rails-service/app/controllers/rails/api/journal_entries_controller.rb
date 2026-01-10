module Rails
  module Api
    class JournalEntriesController < ApplicationController
      include JsonWebTokenAuthenticator

      before_action :authenticate_request, only: %i[create]
      skip_before_action :verify_authenticity_token
      skip_forgery_protection
      
      def create
        source = create_params[:reference_type].constantize.find(create_params[:reference_id])
        journal_entry = JournalEntry::Creator.new(source: source, reversed_by_id: create_params[:reversed_by_id]).call!
        render json: { journal_entry: journal_entry }, status: :ok
      end

      private

      def create_params
        params
          .require(:journal_entry)
          .permit(:reference_id, :reference_type, :reversed_by_id)
      end
    end
  end
end
