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
```
python3 processTrash.py
```
This will process the unread messages in your trash folder.

### 2. Run the processInbox.py script
```
python3 processInbox.py
```
This will process all unread messages in the inbox and find messages that should be removable.

### 3. Run the findRemovable.py script
```
python3 findRemovable.py
```
This will find and present inbox messages that you should investigate.
This may mean:
- Unsubscribing from the relevant list
- Moving the email to the appropriate folder (or trash)


## TODO
- [ ] Find unsub links
    - Parse urls from messages, then get $N$ tokens before and after url. Get embeddings for these tokens, then use dbscan to try to find clusters for unsub links.
    - These messages could then be prioritized as more manageable.
- [ ] Update frontend for presentation
    - Should present links to messages, dollar amounts, maybe neighbor messages
    - [ ] Add button to:
        - [ ] Delete message
        - [ ] Move message to receipts
        - [ ] Find unsub link in body?
