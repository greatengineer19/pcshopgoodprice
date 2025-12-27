class AddPasswordDigestToUser < ActiveRecord::Migration[8.1]
  def change
    add_column :users, :password_digest, :string, if_not_exists: true
  end
end
