class AddReversedByToJournalEntries < ActiveRecord::Migration[8.1]
  def change
    remove_column :journal_entries, :reversed_by_id, if_exists: true
    add_reference :journal_entries,
                  :reversed_by,
                  foreign_key: { to_table: :journal_entries }, if_not_exists: true
  end
end
