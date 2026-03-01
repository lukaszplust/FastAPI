import React from 'react';
import styles from '../App.module.css';

const Sidebar = ({ chatHistory, activeChat, setActiveChat, startNewChat, onDeleteChat}) => {
  return (
    <aside className={styles.sidebar}>
      <button onClick={startNewChat} className={styles.newChatBtn}>
        + New Chat
      </button>
      <div style={{ flex: 1, overflowY: 'auto' }}>
        <p className={styles.recentLabel}>Recent</p>
        {chatHistory.map((item, i) => (
          <div 
            key={i} 
            onClick={() => {
              setActiveChat(item);
              localStorage.setItem("lastActiveChat", item);
            }} 
            className={`${styles.chatItem} ${activeChat === item ? styles.activeChatItem : ''}`}
            style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}
          >
            {/* Nazwa czatu */}
            <span style={{ flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
              {item}
            </span>
            {/* wstawiam przycisk usuwania */}
            <button 
              onClick={(e) => {
                e.stopPropagation(); // zapobiega nadpisaniu lastActiveChat przy usuwaniu!
                onDeleteChat(item);
              }}
              style={{
                background: 'transparent',
                border: 'none',
                color: '#666',
                cursor: 'pointer',
                fontSize: '14px',
                marginLeft: '10px',
                padding: '2px 5px'
              }}
            >
              🗑️
            </button>
          </div>
        ))}
      </div>
    </aside>
  );
};

export default Sidebar;