
function Message(msg) {
    return (
        <div className='message' key={msg.id}>
            <p>
                {msg.Sender}
            </p>
            <p>
                {msg.Subject}
            </p>
            <p>
                {msg.snippet}
            </p>
            <p>
                {msg.url}
            </p>
        </div>
    );
}

export default Message;