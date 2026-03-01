const AuthModal = ({ authData, setAuthData, handleAuth, setIsAuthMode, authError }) => {
    return (
      <div style={{ position: 'fixed', top: 0, left: 0, width: '100vw', height: '100vh', backgroundColor: 'rgba(0,0,0,0.85)', backdropFilter: 'blur(8px)', display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 9999 }}>
        <div style={{ backgroundColor: '#2f2f2f', padding: '40px', borderRadius: '20px', width: '350px', border: '1px solid #444', textAlign: 'center' }}>
          <h2 style={{ marginBottom: '25px' }}>Authentication</h2>
          <input 
            placeholder="Login" 
            onChange={e => setAuthData({...authData, login: e.target.value})} 
            style={{ width: '100%', padding: '12px', marginBottom: '10px', background: '#111', color: 'white', border: '1px solid #444', borderRadius: '8px' }} 
          />
          <input 
            type="password" 
            placeholder="Password" 
            onChange={e => setAuthData({...authData, password: e.target.value})} 
            style={{ width: '100%', padding: '12px', marginBottom: '25px', background: '#111', color: 'white', border: '1px solid #444', borderRadius: '8px' }} 
          />
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            <button onClick={() => handleAuth('login')} style={{ padding: '12px', background: '#fff', color: '#000', fontWeight: 'bold', borderRadius: '8px', cursor: 'pointer' }}>Sign In</button>
            <button onClick={() => handleAuth('register')} style={{ padding: '12px', background: 'transparent', color: '#fff', border: '1px solid #555', borderRadius: '8px', cursor: 'pointer' }}>Create Account</button>
            <button onClick={() => setIsAuthMode(false)} style={{ background: 'none', border: 'none', color: '#888', cursor: 'pointer' }}>Cancel</button>
          </div>
          {authError && <p style={{ color: '#ff4d4d', marginTop: '15px' }}>{authError}</p>}
        </div>
      </div>
    );
  };
  export default AuthModal;