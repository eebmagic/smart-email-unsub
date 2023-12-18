# Smart Email Unsubscribe

This project uses OpenAI embeddings and the Gmail API to match unread email in your trash
(messages you delete without even reading or auto-delete)
with unread email in your inbox
(messages that have flooded your inbox which you haven't opened).
Then a clean list of unread emails in your inbox will be presented, along with unsubscribe links.

This approach attempts to let you quickly clean out your inbox, while also managing email subscriptions to avoid future clutter.

## Dependencies
1. Install python requirements
2. Get a OpenAI API token
3. You may have to delete the gmail token file to regenerate one for your gmail authentication

## Steps to Use

### 1. Run the processTrash.py script
This will process the unread messages in your trash folder.

### 2. Run the processInbox.py script
This will process all unread messages in the inbox and find messages that should be removable.
