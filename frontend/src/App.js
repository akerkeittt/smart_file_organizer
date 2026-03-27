import React, { useState, useEffect, useCallback, useRef } from "react";
import { getFiles, uploadFile, analyzeFile, searchFiles, updateFileTags, openFileLocal, deleteFiles } from "./services/api";
import "./App.css";

/* --- RAW SVGs --- */
const SvgSearch = () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>;
const SvgDashboard = () => <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="3" width="7" height="9"/><rect x="14" y="3" width="7" height="5"/><rect x="14" y="12" width="7" height="9"/><rect x="3" y="16" width="7" height="5"/></svg>;
const SvgDocs = () => <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>;
const SvgReview = () => <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>;
const SvgTags = () => <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"/><line x1="7" y1="7" x2="7.01" y2="7"/></svg>;
const SvgSettings = () => <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>;

/* File specific SVGs */
const SvgPdf = () => <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#ef4444" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>;
const SvgWord = () => <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><path d="M9 12l2 6 2-6" /><path d="M14 12l2 6 2-6" /></svg>;
const SvgTxt = () => <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#9ca3af" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><path d="M12 18v-8M9 10h6"/></svg>;
const SvgDocGeneric = () => <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#a3a3a3" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/><polyline points="13 2 13 9 20 9"/></svg>;

function App() {
  const [activePage, setActivePage] = useState("Documents"); 
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);

  // General State
  const [files, setFiles] = useState([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [activeTab, setActiveTab] = useState("All");

  // Selection & Forms
  const [selectedFile, setSelectedFile] = useState(null);
  const [editTagsList, setEditTagsList] = useState([]);
  const [newTagInput, setNewTagInput] = useState("");
  const [editingTagIndex, setEditingTagIndex] = useState(null);

  // Status flags
  const [uploading, setUploading] = useState(false);
  const [processingFiles, setProcessingFiles] = useState({});
  const [selectedPaths, setSelectedPaths] = useState(new Set());

  // Settings
  const [isLightTheme, setIsLightTheme] = useState(false);
  const [isAutoTagEnabled, setIsAutoTagEnabled] = useState(false);

  const fileInputRef = useRef();

  const loadFiles = useCallback(async () => {
    try {
      if (searchQuery.trim()) {
        const results = await searchFiles(searchQuery);
        setFiles(results);
      } else {
        const data = await getFiles();
        setFiles(data);
      }
    } catch (e) {
      console.error("Error loading files", e);
    }
  }, [searchQuery]);

  useEffect(() => {
    const timer = setTimeout(() => {
      loadFiles();
    }, 300);
    return () => clearTimeout(timer);
  }, [searchQuery, loadFiles, activePage]);

  /* ---- Handlers ---- */
  const handleUpload = async (e) => {
    const selectedFiles = Array.from(e.target.files);
    if (!selectedFiles.length) return;

    setUploading(true);
    let errCount = 0;
    const autoTagQueue = [];
    for (const file of selectedFiles) {
      try {
        const result = await uploadFile(file);
        if (result && result.path) autoTagQueue.push(result.path);
      } catch (err) {
        errCount++;
      }
    }
    setUploading(false);
    
    if (fileInputRef.current) fileInputRef.current.value = "";
    
    await loadFiles();
    
    // Auto tag if enabled
    if (isAutoTagEnabled) {
      for (const path of autoTagQueue) {
         handleGenerateAI(path);
      }
    }
    
    if (errCount > 0) alert(`${errCount} file(s) failed.`);
  };

  const handleGenerateAI = async (filePath) => {
    setProcessingFiles((prev) => ({ ...prev, [filePath]: true }));
    try {
      const result = await analyzeFile(filePath);
      if (!result.tags || result.tags.length === 0) {
        alert("AI could not extract valid text or tags from this file. Please check its contents.");
      }
      setFiles((prev) => prev.map((f) => f.path === filePath ? { ...f, tags: result.tags || [] } : f));
      if (selectedFile && selectedFile.path === filePath) {
        setSelectedFile((prev) => ({ ...prev, tags: result.tags || [] }));
        setEditTagsList(result.tags || []);
      }
    } catch (e) {
      alert("AI task failed. Ensure local models are running.");
    }
    setProcessingFiles((prev) => ({ ...prev, [filePath]: false }));
  };

  const handleOpenFile = async (filePath) => {
    try {
      const result = await openFileLocal(filePath);
      if (result.error) alert("Could not open file: " + result.error);
    } catch (e) {}
  };

  const toggleSelection = (path) => {
    const newSet = new Set(selectedPaths);
    if (newSet.has(path)) newSet.delete(path);
    else newSet.add(path);
    setSelectedPaths(newSet);
  };

  const toggleAll = () => {
    if (selectedPaths.size === getFilteredFiles().length && getFilteredFiles().length > 0) {
      setSelectedPaths(new Set());
    } else {
      setSelectedPaths(new Set(getFilteredFiles().map(f => f.path)));
    }
  };

  const handleBulkDelete = async () => {
    if (!window.confirm(`Delete ${selectedPaths.size} file(s) permanently?`)) return;
    try {
      await deleteFiles(Array.from(selectedPaths));
      setSelectedPaths(new Set());
      await loadFiles();
    } catch (e) {
      alert("Failed to safely delete files.");
    }
  };

  const handleSingleDelete = async (filePath) => {
    if (!window.confirm("Permanently delete this file via actions?")) return;
    try {
      await deleteFiles([filePath]);
      const newSet = new Set(selectedPaths);
      newSet.delete(filePath);
      setSelectedPaths(newSet);
      if (selectedFile?.path === filePath) setSelectedFile(null);
      await loadFiles();
    } catch (e) {
      alert("Failed to delete file.");
    }
  };

  const handleBulkTag = async () => {
    const paths = Array.from(selectedPaths);
    for (const path of paths) {
      if (!processingFiles[path]) {
        // Run AI on queue without awaiting so they load concurrently, or await for sequential
        handleGenerateAI(path); // Sequential triggers independently
      }
    }
    setSelectedPaths(new Set()); // deselect after starting
  };

  const getFilteredFiles = () => {
    if (activeTab === "All") return files;
    if (activeTab === "PDFs") return files.filter(f => f.name.toLowerCase().endsWith(".pdf"));
    if (activeTab === "Word") return files.filter(f => f.name.toLowerCase().includes(".doc"));
    if (activeTab === "Text") return files.filter(f => f.name.toLowerCase().endsWith(".txt"));
    return files;
  };

  const handleSelectFile = (file) => {
    if (selectedFile?.path === file.path) { closeDetailsPanel(); return; }
    setSelectedFile(file);
    setEditTagsList([...(file.tags || [])]);
    setNewTagInput("");
    setEditingTagIndex(null);
  };

  const closeDetailsPanel = () => setSelectedFile(null);
  const handleRemoveEditTag = (i) => setEditTagsList(prev => prev.filter((_, idx) => idx !== i));
  const handleAddEditTag = (e) => {
    e.preventDefault();
    const tag = newTagInput.trim().toLowerCase();
    if (tag && !editTagsList.includes(tag)) setEditTagsList([...editTagsList, tag]);
    setNewTagInput("");
  };
  const startEditingTag = (i) => setEditingTagIndex(i);
  const handleTagChange = (e, i) => {
    const newTags = [...editTagsList];
    newTags[i] = e.target.value.toLowerCase();
    setEditTagsList(newTags);
  };
  const finishEditingTag = (i) => {
    setEditingTagIndex(null);
    if (!editTagsList[i].trim()) handleRemoveEditTag(i);
  };
  const handleSaveChanges = async () => {
    if (!selectedFile) return;
    try {
      const finalTags = editTagsList.map(t => t.trim()).filter(t => t.length > 0);
      const result = await updateFileTags(selectedFile.path, finalTags);
      setFiles((prev) => prev.map((f) => f.path === selectedFile.path ? { ...f, tags: result.tags } : f));
      setSelectedFile({ ...selectedFile, tags: result.tags });
      setEditTagsList(result.tags);
    } catch (e) {}
  };

  const handleTagCloudClick = (tag) => {
    setSearchQuery(tag);
    setActivePage("Documents");
  };

  const renderSidebarItem = (pageName, IconComp) => (
    <button className={`nav-item ${activePage === pageName ? 'active' : ''}`} onClick={() => { setActivePage(pageName); setSelectedFile(null); setSearchQuery(""); }}>
      <span className="nav-icon"><IconComp /></span>
      {!isSidebarOpen ? null : <span>{pageName}</span>}
    </button>
  );

  const getDynamicIcon = (filename) => {
    const lower = filename.toLowerCase();
    if (lower.endsWith('.pdf')) return <SvgPdf />;
    if (lower.includes('.doc')) return <SvgWord />;
    if (lower.endsWith('.txt')) return <SvgTxt />;
    return <SvgDocGeneric />;
  };

  // Computations
  const totalTags = files.reduce((acc, f) => acc + (f.tags ? f.tags.length : 0), 0);
  const untaggedFiles = files.filter(f => !f.tags || f.tags.length === 0);
  
  const allTagsSet = new Set();
  files.forEach(f => { if(f.tags) f.tags.forEach(t => allTagsSet.add(t)) });
  const allUniqueTags = Array.from(allTagsSet);

  return (
    <div className={`app-container ${isLightTheme ? 'light-theme' : ''}`}>
      {uploading && <div className="importing-overlay"><div className="spinner-box"><div className="spinner"></div><p>Importing files into library...</p></div></div>}
      {Object.values(processingFiles).some(Boolean) && <div className="analyzing-overlay"><div className="spinner-box"><div className="spinner"></div><p>AI is reading documents and creating tags...</p></div></div>}

      <aside className={`sidebar ${!isSidebarOpen ? 'collapsed' : ''}`}>
        <button className="sidebar-toggle" onClick={() => setIsSidebarOpen(!isSidebarOpen)}>
          {isSidebarOpen ? '<' : '>'}
        </button>
        <div className="brand">
          <div className="brand-wrapper">
            <div className="brand-logo">S</div>
            <span className="brand-name">Smart Organizer</span>
          </div>
        </div>
        <nav className="nav-menu">
          {renderSidebarItem("Dashboard", SvgDashboard)}
          {renderSidebarItem("Documents", SvgDocs)}
          {renderSidebarItem("Pending", SvgReview)}
          {renderSidebarItem("Tags", SvgTags)}
          {renderSidebarItem("Settings", SvgSettings)}
        </nav>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div className="search-wrap" style={{ visibility: activePage === "Documents" ? "visible" : "hidden" }}>
            <span className="search-icon"><SvgSearch /></span>
            <input type="text" className="search-input" placeholder="Search documents by name or tag..." value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)} />
          </div>
          {activePage === "Documents" && (
            <label className={`btn btn-primary ${uploading ? 'disabled' : ''}`}>
              + Import Files
              <input type="file" multiple accept=".txt,.pdf,.doc,.docx" onChange={handleUpload} disabled={uploading} ref={fileInputRef} hidden />
            </label>
          )}
        </header>

        <div className="content-body">
          {activePage === "Settings" ? (
            <div className="dummy-page">
              <h1 className="page-title">Settings</h1>
              <div className="settings-group">
                <h3>General Preferences</h3>
                <div className="setting-row">
                  <span>Light Theme</span>
                  <div className={`toggle-switch ${isLightTheme ? 'on' : ''}`} onClick={() => setIsLightTheme(!isLightTheme)}>
                    <div className="toggle-head"></div>
                  </div>
                </div>
                <div className="setting-row">
                  <span>Auto-Tag on Import</span>
                  <div className={`toggle-switch ${isAutoTagEnabled ? 'on' : ''}`} onClick={() => setIsAutoTagEnabled(!isAutoTagEnabled)}>
                    <div className="toggle-head"></div>
                  </div>
                </div>
              </div>
            </div>
          ) : activePage === "Pending" ? (
            <div className="dummy-page">
              <h1 className="page-title">Pending Tags</h1>
              <p style={{marginBottom: "20px", color: isLightTheme ? "#4b5563" : "#a3a3a3"}}>Files waiting for processing</p>
              <div className="recent-activity">
                <div className="activity-list">
                  {untaggedFiles.length === 0 ? <p style={{color: isLightTheme ? "#9ca3af" : "#525252"}}>No files pending tags.</p> : 
                   untaggedFiles.map((f, i) => <div key={i} className="activity-item"><span>{f.name}</span> <span style={{color: isLightTheme ? "#9ca3af" : "#525252"}}>Missing Tags</span></div>)
                  }
                </div>
              </div>
            </div>
          ) : activePage === "Tags" ? (
            <div className="dummy-page">
              <h1 className="page-title">Global Tag Dictionary</h1>
              <div className="tags-cloud">
               {allUniqueTags.length === 0 ? <p style={{color: isLightTheme ? "#9ca3af" : "#525252"}}>No tags generated yet.</p> :
                  allUniqueTags.map((tag, i) => <span key={i} className="cloud-tag" onClick={() => handleTagCloudClick(tag)}>{tag}</span>)
               }
              </div>
            </div>
          ) : activePage === "Dashboard" ? (
            <div className="dummy-page">
              <h1 className="page-title">Analytics</h1>
              <div className="dashboard-stats">
                <div className="stat-card">
                  <span className="stat-title">Total Documents</span>
                  <span className="stat-value">{files.length}</span>
                </div>
                <div className="stat-card">
                  <span className="stat-title">Generated Tags</span>
                  <span className="stat-value">{totalTags}</span>
                </div>
                <div className="stat-card">
                  <span className="stat-title">Pending Analysis</span>
                  <span className="stat-value">{untaggedFiles.length}</span>
                </div>
              </div>
              <div className="recent-activity">
                <h3>Library Composition</h3>
                <div className="activity-list">
                  <div className="activity-item"><span>PDF Documents</span> <span>{files.filter(f => f.name.toLowerCase().endsWith('.pdf')).length}</span></div>
                  <div className="activity-item"><span>Word Documents</span> <span>{files.filter(f => f.name.toLowerCase().includes('.doc')).length}</span></div>
                  <div className="activity-item"><span>Text Files</span> <span>{files.filter(f => f.name.toLowerCase().endsWith('.txt')).length}</span></div>
                </div>
              </div>
            </div>
          ) : (
            <>
              <h1 className="page-title">All Documents</h1>
              <div className="tabs">
                {["All", "PDFs", "Word", "Text"].map(tab => (
                  <button key={tab} className={`tab ${activeTab === tab ? 'active' : ''}`} onClick={() => setActiveTab(tab)}>{tab}</button>
                ))}
              </div>

              {selectedPaths.size > 0 && (
                <div className="bulk-actions-bar">
                  <span className="bulk-actions-info">{selectedPaths.size} document(s) selected</span>
                  <div style={{display:'flex', gap:'8px'}}>
                     <button className="btn btn-outline btn-small" onClick={handleBulkTag}>Tag Selected</button>
                     <button className="btn btn-danger btn-small" onClick={handleBulkDelete}>Delete Selected</button>
                     <button className="btn btn-outline btn-small" onClick={() => setSelectedPaths(new Set())}>Cancel</button>
                  </div>
                </div>
              )}

              <div className="table-wrapper">
                <table className="file-table">
                  <thead>
                    <tr>
                      <th className="chk-cell">
                        <input type="checkbox" checked={getFilteredFiles().length > 0 && selectedPaths.size === getFilteredFiles().length} onChange={toggleAll} />
                      </th>
                      <th>Name</th>
                      <th>Tags</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {getFilteredFiles().length === 0 ? (
                      <tr className="file-row"><td colSpan="4" className="empty-state">Workspace is empty.</td></tr>
                    ) : (
                      getFilteredFiles().map((file, idx) => {
                        const isSelected = selectedPaths.has(file.path);
                        const hasTags = file.tags && file.tags.length > 0;
                        return (
                          <tr key={idx} className={`file-row ${selectedFile?.path === file.path ? 'selected' : ''}`} onClick={() => handleSelectFile(file)}>
                            <td className="chk-cell" onClick={(e) => { e.stopPropagation(); toggleSelection(file.path) }}>
                              <input type="checkbox" checked={isSelected} onChange={() => {}} />
                            </td>
                            <td className="cell-name">
                              <div className="name-content">
                                <span className="icon">{getDynamicIcon(file.name)}</span>
                                <span>{file.name}</span>
                              </div>
                            </td>
                            <td>
                              <div className="tags-flex">
                                {hasTags ? (
                                  file.tags.map((tag, i) => <span key={i} className="tag-badge">{tag}</span>)
                                ) : (
                                  <span className="tag-placeholder">Not tagged</span>
                                )}
                              </div>
                            </td>
                            <td className="cell-actions">
                              <div className="actions-flex">
                                <button className="btn btn-outline btn-small" onClick={(e) => { e.stopPropagation(); handleOpenFile(file.path); }}>Open</button>
                                <button className="btn btn-outline btn-small btn-tag-action" onClick={(e) => { e.stopPropagation(); handleGenerateAI(file.path); }} disabled={processingFiles[file.path]}>
                                  {processingFiles[file.path] ? "Analyz..." : (hasTags ? "Retag" : "Tag")}
                                </button>
                                <button className="btn btn-danger btn-small" onClick={(e) => { e.stopPropagation(); handleSingleDelete(file.path); }}>Delete</button>
                              </div>
                            </td>
                          </tr>
                        )
                      })
                    )}
                  </tbody>
                </table>
              </div>
            </>
          )}
        </div>
      </main>

      <aside className={`details-panel ${!selectedFile || activePage !== "Documents" ? 'hidden' : ''}`}>
        {!selectedFile ? null : (
          <div className="details-content">
            <div className="details-header">
              <div className="details-header-top">
                <h2 className="file-title">{selectedFile.name}</h2>
                <button className="btn-close-panel" onClick={closeDetailsPanel}>×</button>
              </div>
              <p className="file-meta">Click any tag below to edit</p>
            </div>

            <div className="tags-section">
              <label className="section-label">Tags Editor</label>
              <div className="edit-tags-list">
                {editTagsList.length === 0 ? (
                  <p className="no-tags-text">Empty. Add tags below.</p>
                ) : (
                  editTagsList.map((tag, idx) => (
                    <div key={idx} className="edit-tag-wrapper">
                      {editingTagIndex === idx ? (
                        <input autoFocus className="tag-edit-input" value={tag} onChange={(e) => handleTagChange(e, idx)} onBlur={() => finishEditingTag(idx)} onKeyDown={(e) => { if (e.key === 'Enter') finishEditingTag(idx) }} />
                      ) : (
                        <div className="edit-tag" onClick={() => startEditingTag(idx)}>{tag}</div>
                      )}
                      <button className="btn-remove-tag" onClick={() => handleRemoveEditTag(idx)}>×</button>
                    </div>
                  ))
                )}
              </div>
              <form className="add-tag-form" onSubmit={handleAddEditTag}>
                <input type="text" className="input-field" placeholder="Add tag + Enter" value={newTagInput} onChange={(e) => setNewTagInput(e.target.value)} />
              </form>
            </div>

            <div className="details-footer">
              <button className="btn btn-primary full-width" onClick={handleSaveChanges}>
                Save
              </button>
            </div>
          </div>
        )}
      </aside>
    </div>
  );
}

export default App;
