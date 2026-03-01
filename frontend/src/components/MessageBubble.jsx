const MessageBubble = ({ msg }) => {
    const isUser = msg.role === 'user';
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: isUser ? 'flex-end' : 'flex-start', 
        padding: '12px 20px' 
      }}>
        <div style={{ 
          maxWidth: '80%', 
          padding: '12px 18px', 
          borderRadius: '20px', 
          backgroundColor: isUser ? '#3d3d3d' : 'transparent', 
          border: isUser ? 'none' : '1px solid #333' 
        }}>
          <div style={{ fontSize: '10px', fontWeight: 'bold', marginBottom: '4px', color: '#666' }}>
            {msg.role.toUpperCase()}
          </div>
          {msg.content}
        </div>
      </div>
    );
  };
  export default MessageBubble;