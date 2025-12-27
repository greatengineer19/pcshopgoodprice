class RemoveBrokenReversedByFromJournalEntries < ActiveRecord::Migration[8.1]
  def change
    remove_index :journal_entries,
                 name: "index_journal_entries_on_{to_table: :journal_entries}_id", if_exists: true

    remove_column :journal_entries,
                  "{to_table: :journal_entries}_id",
                  :bigint, if_exists: true
  end
end
