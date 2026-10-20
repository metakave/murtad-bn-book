import React, { useState, useEffect } from 'react';
import { 
  BookOpen, 
  List, 
  User, 
  Home as HomeIcon, 
  Type, 
  Sun, 
  Moon, 
  Bookmark, 
  ChevronRight, 
  ChevronLeft,
  Share2,
  CheckCircle,
  Search,
  BookMarked,
  Clock,
  Sparkles,
  X
} from 'lucide-react';
import bookData from './book_data.json';

// Bengali numeral converter helper
const toBnNum = (n) => {
  if (n === null || n === undefined) return '';
  const bnDigits = ['০', '১', '২', '৩', '৪', '৫', '৬', '৭', '৮', '৯'];
  return String(n).replace(/[0-9]/g, (d) => bnDigits[Number(d)]);
};

export default function App() {
  const getStorageItem = (key, fallback) => {
    try {
      const val = localStorage.getItem(key);
      return val !== null ? val : fallback;
    } catch {
      return fallback;
    }
  };

  const setStorageItem = (key, val) => {
    try {
      localStorage.setItem(key, val);
    } catch {}
  };

  const [activeTab, setActiveTab] = useState('home'); // home | reader | toc | profile
  const [theme, setTheme] = useState(() => getStorageItem('reader-theme', 'sepia'));
  const [fontSize, setFontSize] = useState(() => Number(getStorageItem('reader-font-size', 19)) || 19);
  const [lineHeight, setLineHeight] = useState(() => Number(getStorageItem('reader-line-height', 1.85)) || 1.85);
  const [fontFamily, setFontFamily] = useState(() => getStorageItem('reader-font-family', 'serif'));
  const [currentChapterIndex, setCurrentChapterIndex] = useState(() => {
    const saved = Number(getStorageItem('reader-last-chapter', 0));
    return isNaN(saved) ? 0 : saved;
  });
  const [showSettingsSheet, setShowSettingsSheet] = useState(false);
  const [showRegisterModal, setShowRegisterModal] = useState(false);
  const [userProfile, setUserProfile] = useState(() => {
    try {
      const raw = getStorageItem('reader-user-profile', null);
      return raw ? JSON.parse(raw) : null;
    } catch {
      return null;
    }
  });
  const [searchQuery, setSearchQuery] = useState('');
  const [readingProgress, setReadingProgress] = useState(0);

  // Compute actual total words across all chapters
  const totalWordCount = React.useMemo(() => {
    if (!bookData?.chapters) return 0;
    return bookData.chapters.reduce((total, ch) => {
      if (!ch.paragraphs) return total;
      return total + ch.paragraphs.reduce((pTot, p) => pTot + (p ? p.trim().split(/\s+/).filter(Boolean).length : 0), 0);
    }, 0);
  }, []);

  // Apply Theme & Font attributes to DOM
  useEffect(() => {
    try {
      document.documentElement.setAttribute('data-theme', theme);
      setStorageItem('reader-theme', theme);
    } catch {}
  }, [theme]);

  useEffect(() => {
    setStorageItem('reader-font-size', fontSize);
    setStorageItem('reader-line-height', lineHeight);
    setStorageItem('reader-font-family', fontFamily);
  }, [fontSize, lineHeight, fontFamily]);

  useEffect(() => {
    setStorageItem('reader-last-chapter', currentChapterIndex);
    try {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch {}
  }, [currentChapterIndex]);

  // Track scroll progress in reader
  useEffect(() => {
    const handleScroll = () => {
      if (activeTab !== 'reader') return;
      const totalHeight = document.documentElement.scrollHeight - window.innerHeight;
      if (totalHeight <= 0) return;
      const progress = Math.min(100, Math.round((window.scrollY / totalHeight) * 100));
      setReadingProgress(progress);
    };
    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, [activeTab]);

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formError, setFormError] = useState('');

  const currentChapter = bookData.chapters[currentChapterIndex] || bookData.chapters[0];

  // Gated Start Reading handler
  const handleStartReading = () => {
    if (userProfile) {
      setActiveTab('reader');
    } else {
      setShowRegisterModal(true);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setFormError('');
    setIsSubmitting(true);

    const formData = new FormData(e.target);
    const name = formData.get('name')?.toString().trim();
    const whatsapp = formData.get('whatsapp')?.toString().trim();
    const email = formData.get('email')?.toString().trim();
    const city = formData.get('city')?.toString().trim();

    if (!name || !whatsapp || !email || !city) {
      setFormError('দয়া করে সবগুলো তথ্য সঠিকভাবে পূরণ করুন।');
      setIsSubmitting(false);
      return;
    }

    try {
      // Post registration to local server to append to readers.csv
      const res = await fetch('/api/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, whatsapp, email, city })
      });

      if (!res.ok) {
        const errJson = await res.json().catch(() => ({}));
        throw new Error(errJson.error || 'নিবন্ধন সংরক্ষণ ব্যর্থ হয়েছে');
      }

      const profile = {
        name,
        whatsapp,
        email,
        city,
        registeredAt: new Date().toLocaleDateString('bn-BD')
      };

      setStorageItem('reader-user-profile', JSON.stringify(profile));
      setUserProfile(profile);
      setShowRegisterModal(false);
      setActiveTab('reader'); // Grant immediate access to reading
    } catch (err) {
      console.error(err);
      setFormError('সার্ভারে তথ্য সংরক্ষণ করতে সমস্যা হচ্ছে। আবার চেষ্টা করুন।');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="app-shell" style={{
      '--reader-font-size': `${fontSize}px`,
      '--line-height': lineHeight,
      fontFamily: fontFamily === 'serif' ? 'var(--font-serif)' : 'var(--font-sans)'
    }}>
      {/* Top Header */}
      <header className="top-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flex: 1, minWidth: 0 }}>
          {activeTab === 'reader' && (
            <button 
              className="icon-btn" 
              onClick={() => setActiveTab('toc')}
              title="Table of Contents"
            >
              <List size={18} />
            </button>
          )}
          <h1 className="header-title">
            {activeTab === 'home' && 'কুরআনে মুরতাদ হত্যার অবৈধতা'}
            {activeTab === 'reader' && currentChapter.title}
            {activeTab === 'toc' && 'সূচিপত্র'}
            {activeTab === 'profile' && 'প্রোফাইল ও সেটিংস'}
          </h1>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <button 
            className="icon-btn" 
            onClick={() => setShowSettingsSheet(true)}
            title="পড়ার ফন্ট ও থিম সেটিংস"
          >
            <Type size={18} />
          </button>
        </div>
      </header>

      {/* Reader Progress Bar (Top) */}
      {activeTab === 'reader' && (
        <div style={{
          position: 'sticky',
          top: '57px',
          left: 0,
          right: 0,
          height: '3px',
          background: 'var(--border)',
          zIndex: 39
        }}>
          <div style={{
            height: '100%',
            width: `${readingProgress}%`,
            background: 'var(--accent)',
            transition: 'width 0.1s ease'
          }} />
        </div>
      )}

      {/* Main Content Area */}
      <main className="main-content">
        {/* TAB 1: HOME */}
        {activeTab === 'home' && (
          <div style={{ padding: '24px 20px' }}>
            {/* Book Cover Banner Card */}
            <div style={{
              background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 100%)',
              borderRadius: '24px',
              padding: '28px 20px',
              color: '#ffffff',
              position: 'relative',
              overflow: 'hidden',
              boxShadow: '0 12px 30px rgba(15, 23, 42, 0.25)',
              marginBottom: '24px'
            }}>
              <div style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '6px',
                background: 'rgba(255, 255, 255, 0.15)',
                padding: '4px 12px',
                borderRadius: '20px',
                fontSize: '12px',
                marginBottom: '16px',
                backdropFilter: 'blur(8px)'
              }}>
                <Sparkles size={13} color="#f59e0b" />
                <span>প্রামাণ্য গবেষণা গ্রন্থ</span>
              </div>

              <h2 style={{
                fontFamily: 'var(--font-serif)',
                fontSize: '24px',
                fontWeight: 700,
                lineHeight: 1.35,
                marginBottom: '10px'
              }}>
                {bookData.title}
              </h2>

              <p style={{
                fontFamily: 'var(--font-ui)',
                fontSize: '13px',
                opacity: 0.8,
                marginBottom: '20px'
              }}>
                {bookData.englishTitle}
              </p>

              <div style={{
                borderTop: '1px solid rgba(255, 255, 255, 0.12)',
                paddingTop: '16px',
                display: 'flex',
                flexDirection: 'column',
                gap: '6px',
                fontSize: '13px',
                opacity: 0.9
              }}>
                <div><strong>গবেষক ও সংকলক:</strong> {bookData.compiler}</div>
                <div><strong>সম্পাদনা:</strong> {bookData.editor}</div>
                <div><strong>প্রকাশনা:</strong> {bookData.publisher}</div>
              </div>

              <div style={{ marginTop: '24px', display: 'flex', gap: '12px' }}>
                <button 
                  className="primary-btn" 
                  style={{ flex: 1, padding: '14px', fontSize: '16px' }}
                  onClick={handleStartReading}
                >
                  <BookOpen size={19} />
                  <span>পড়া শুরু করুন</span>
                </button>
              </div>
            </div>

            {/* Quick Stats Grid */}
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(3, 1fr)',
              gap: '12px',
              marginBottom: '24px'
            }}>
              <div style={{
                background: 'var(--bg-card)',
                padding: '16px 12px',
                borderRadius: '16px',
                textAlign: 'center',
                border: '1px solid var(--border)'
              }}>
                <div style={{ fontSize: '20px', fontWeight: 700, color: 'var(--accent)', fontFamily: 'var(--font-sans)' }}>
                  {toBnNum(bookData.totalChapters)}
                </div>
                <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '4px' }}>
                  মোট অধ্যায়
                </div>
              </div>

              <div style={{
                background: 'var(--bg-card)',
                padding: '16px 12px',
                borderRadius: '16px',
                textAlign: 'center',
                border: '1px solid var(--border)'
              }}>
                <div style={{ fontSize: '20px', fontWeight: 700, color: 'var(--accent)', fontFamily: 'var(--font-sans)' }}>
                  {toBnNum(totalWordCount.toLocaleString('en-US'))}
                </div>
                <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '4px' }}>
                  মোট শব্দ
                </div>
              </div>

              <div style={{
                background: 'var(--bg-card)',
                padding: '16px 12px',
                borderRadius: '16px',
                textAlign: 'center',
                border: '1px solid var(--border)'
              }}>
                <div style={{ fontSize: '20px', fontWeight: 700, color: 'var(--accent)', fontFamily: 'var(--font-sans)' }}>
                  ১০০%
                </div>
                <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '4px' }}>
                  কুরআনিক রেফারেন্স
                </div>
              </div>
            </div>

            {/* Resume Last Read Card */}
            <div 
              onClick={handleStartReading}
              style={{
                background: 'var(--bg-surface)',
                borderRadius: '18px',
                padding: '18px',
                border: '1px solid var(--border)',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                marginBottom: '24px',
                boxShadow: 'var(--shadow)'
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
                <div style={{
                  background: 'var(--accent-light)',
                  color: 'var(--accent)',
                  width: '46px',
                  height: '46px',
                  borderRadius: '14px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}>
                  <BookMarked size={22} />
                </div>
                <div>
                  <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                    সর্বশেষ যেখানে ছিলেন (অধ্যায় {toBnNum(currentChapterIndex + 1)})
                  </div>
                  <div style={{ fontSize: '16px', fontWeight: 600, marginTop: '2px', color: 'var(--text-primary)' }}>
                    {currentChapter.title}
                  </div>
                </div>
              </div>
              <ChevronRight size={20} color="var(--text-muted)" />
            </div>

            {/* Overview / Blurb */}
            <div style={{
              background: 'var(--bg-surface)',
              borderRadius: '18px',
              padding: '20px',
              border: '1px solid var(--border)',
              lineHeight: 1.8
            }}>
              <h3 style={{ fontSize: '17px', fontWeight: 700, marginBottom: '10px' }}>
                বইটি সম্পর্কে সারসংক্ষেপ
              </h3>
              <p style={{ fontSize: '15px', color: 'var(--text-secondary)', textAlign: 'justify' }}>
                মুসলিম বিশ্বে বহুল আলোচিত ও বিতর্কিত ব্লাসফেমী ও মুরতাদ হত্যা আইনের মূল ভিত্তি কী এবং আল-কুরআনের দ্ব্যর্থহীন নির্দেশনায় ধর্মীয় স্বাধীনতা, মানুষের চিন্তার স্বাধীনতা এবং ঈমান ও কুফরের জবাবদিহিতা কীভাবে নির্ধারিত হয়েছে—এই গ্রন্থে প্রতিটি যুক্তি ও দলীল পুঙ্খানুপুঙ্খভাবে নির্মোহ বিশ্লেষণের সাথে তুলে ধরা হয়েছে।
              </p>
            </div>
          </div>
        )}

        {/* TAB 2: READER */}
        {activeTab === 'reader' && (
          <div style={{ padding: '24px 20px 40px' }}>
            {/* Chapter Header Card */}
            <div style={{
              textAlign: 'center',
              padding: '20px 10px 30px',
              borderBottom: '1px solid var(--border)',
              marginBottom: '28px'
            }}>
              <div style={{
                fontSize: '13px',
                color: 'var(--accent)',
                fontWeight: 600,
                letterSpacing: '0.05em',
                marginBottom: '6px',
                fontFamily: 'var(--font-sans)'
              }}>
                অধ্যায় {toBnNum(currentChapterIndex + 1)} / {toBnNum(bookData.chapters.length)}
              </div>

              <h2 style={{
                fontFamily: 'var(--font-serif)',
                fontSize: '26px',
                fontWeight: 700,
                lineHeight: 1.4,
                color: 'var(--text-primary)',
                marginBottom: '10px'
              }}>
                {currentChapter.title}
              </h2>

              <div style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '6px',
                fontSize: '12px',
                color: 'var(--text-muted)',
                fontFamily: 'var(--font-sans)'
              }}>
                <Clock size={13} />
                <span>পড়ার সময়: প্রায় {toBnNum(currentChapter.readTimeMinutes)} মিনিট</span>
              </div>
            </div>

            {/* Chapter Paragraphs */}
            <div className="reader-text">
              {currentChapter.paragraphs && currentChapter.paragraphs.map((para, idx) => {
                let chapterNumBlock = null;
                let chapterTitleBlock = null;
                let contentText = para;

                // Check if paragraph starts with an in-text chapter label like "অধ্যায় ১", "অধ্যায় ৪", etc.
                const chMatch = contentText.match(/^(অধ্যায়\s+[০-৯\d]+)(?:\s+(.*))?$/s);
                if (chMatch) {
                  chapterNumBlock = (
                    <h3 className="chapter-heading-h3">
                      {toBnNum(chMatch[1].trim())}
                    </h3>
                  );
                  contentText = chMatch[2]?.trim() || '';
                }

                // If this is paragraph 0 and starts with the chapter title (or title appears after অধ্যায় X), render title as H3
                if (idx === 0 && currentChapter.title) {
                  const normTitle = currentChapter.title.replace(/'/g, '’').trim();
                  const normContent = contentText.replace(/'/g, '’').trim();
                  if (normContent.startsWith(normTitle)) {
                    chapterTitleBlock = (
                      <h3 className="chapter-title-h3">
                        {currentChapter.title}
                      </h3>
                    );
                    contentText = normContent.slice(normTitle.length).trim();
                  }
                }

                if (!contentText && (chapterNumBlock || chapterTitleBlock)) {
                  return (
                    <React.Fragment key={idx}>
                      {chapterNumBlock}
                      {chapterTitleBlock}
                    </React.Fragment>
                  );
                }

                // Split text so that every Quranic verse citation (e.g. ৫:১০৫ ::, ১৩:৩১ ::, ৭৪:৫৪-৫৫ ::) starts in a new line
                const versePattern = /([০-৯\d]+[:ঃ][০-৯\d]+(?:\s*-\s*[০-৯\d]+)?\s*::)/g;
                const tokens = contentText.split(versePattern);

                const segments = [];
                if (tokens[0] && tokens[0].trim()) {
                  segments.push({ type: 'text', content: tokens[0].trim() });
                }

                for (let i = 1; i < tokens.length; i += 2) {
                  const citation = tokens[i].trim();
                  const body = tokens[i + 1] ? tokens[i + 1].trim() : '';
                  segments.push({
                    type: 'verse',
                    citation: toBnNum(citation.replace('::', '').trim()),
                    content: body
                  });
                }

                return (
                  <React.Fragment key={idx}>
                    {chapterNumBlock}
                    {chapterTitleBlock}
                    {segments.map((seg, sIdx) => {
                      if (seg.type === 'verse') {
                        return (
                          <div key={sIdx} className="quran-verse">
                            <span className="verse-citation-badge">{seg.citation}</span>{' '}
                            <span>{seg.content}</span>
                          </div>
                        );
                      }
                      // If this is Chapter 18 (পরিভাষা) and starts with a term before colon, render term in bold
                      const colonIdx = seg.content.indexOf(':');
                      if (colonIdx > 0 && colonIdx < 40 && (currentChapter.id === 'terminology' || currentChapterIndex === 17)) {
                        const termPart = seg.content.slice(0, colonIdx + 1);
                        const descPart = seg.content.slice(colonIdx + 1).trim();
                        return (
                          <p key={sIdx} style={{ marginTop: '1.2em' }}>
                            <strong className="terminology-term-bold">{termPart}</strong>
                            <span>{descPart}</span>
                          </p>
                        );
                      }

                      // If this is Chapter 19 (তথ্যসুত্র ও গ্রন্থপঞ্জি), format each book/source neatly on its own line
                      if (currentChapter.id === 'bibliography' || currentChapterIndex === 18) {
                        const isSubheading = seg.content.includes('প্রকাশিত বইসমূহ');
                        const isNumberedBook = /^[০-৯\d]+\./.test(seg.content.trim());
                        return (
                          <p 
                            key={sIdx} 
                            style={{ 
                              marginBottom: isSubheading ? '12px' : '8px',
                              marginTop: isSubheading ? '18px' : '0',
                              fontWeight: isSubheading ? 700 : 400,
                              fontSize: isSubheading ? '17px' : '15px',
                              paddingLeft: isNumberedBook ? '12px' : '0',
                              borderLeft: isNumberedBook ? '3px solid var(--primary-light)' : 'none',
                              lineHeight: 1.6
                            }}
                          >
                            {seg.content}
                          </p>
                        );
                      }

                      // If this is Chapter 16 (মুরতাদ হত্যা প্রসঙ্গে উপস্থাপিত হাদীসের পর্যালোচনা), format hadith quotes and analysis headers
                      if (currentChapter.id === 'hadith_review' || currentChapterIndex === 15) {
                        if (seg.content.startsWith('১. ') || seg.content.startsWith('২. ')) {
                          const num = seg.content.slice(0, 3);
                          const text = seg.content.slice(3);
                          return (
                            <div key={sIdx} className="hadith-quote-box">
                              <span className="hadith-badge">হাদীস {toBnNum(num.trim())}</span>{' '}
                              <span>{text}</span>
                            </div>
                          );
                        }
                        if (seg.content.startsWith('পর্যালোচনা:')) {
                          const heading = 'পর্যালোচনা:';
                          const text = seg.content.slice(heading.length).trim();
                          return (
                            <div key={sIdx} style={{ marginTop: '1.2em' }}>
                              <h4 className="analysis-heading">{heading}</h4>
                              <p>{text}</p>
                            </div>
                          );
                        }
                      }

                      return (
                        <p key={sIdx}>
                          {seg.content}
                        </p>
                      );
                    })}
                  </React.Fragment>
                );
              })}
            </div>

            {/* Bottom Chapter Switcher Navigation */}
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginTop: '40px',
              paddingTop: '20px',
              borderTop: '1px solid var(--border)',
              gap: '12px'
            }}>
              <button
                className="icon-btn"
                style={{ width: 'auto', padding: '10px 16px', borderRadius: '12px', gap: '6px' }}
                disabled={currentChapterIndex === 0}
                onClick={() => setCurrentChapterIndex(prev => Math.max(0, prev - 1))}
              >
                <ChevronLeft size={18} />
                <span>পূর্ববর্তী</span>
              </button>

              <button
                className="primary-btn"
                style={{ padding: '10px 20px', borderRadius: '12px' }}
                disabled={currentChapterIndex >= bookData.chapters.length - 1}
                onClick={() => setCurrentChapterIndex(prev => Math.min(bookData.chapters.length - 1, prev + 1))}
              >
                <span>পরবর্তী অধ্যায়</span>
                <ChevronRight size={18} />
              </button>
            </div>
          </div>
        )}

        {/* TAB 3: TABLE OF CONTENTS (TOC) */}
        {activeTab === 'toc' && (
          <div style={{ padding: '20px' }}>
            {/* Search Input */}
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '10px',
              background: 'var(--bg-surface)',
              border: '1px solid var(--border)',
              borderRadius: '14px',
              padding: '12px 16px',
              marginBottom: '20px'
            }}>
              <Search size={18} color="var(--text-muted)" />
              <input
                type="text"
                placeholder="অধ্যায়ের শিরোনাম খুঁজুন..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                style={{
                  background: 'transparent',
                  border: 'none',
                  outline: 'none',
                  color: 'var(--text-primary)',
                  fontFamily: 'var(--font-sans)',
                  fontSize: '15px',
                  width: '100%'
                }}
              />
              {searchQuery && (
                <button 
                  onClick={() => setSearchQuery('')}
                  style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-muted)' }}
                >
                  <X size={16} />
                </button>
              )}
            </div>

            {/* Chapter List */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {bookData.chapters
                .map((ch, originalIdx) => ({ ...ch, originalIdx }))
                .filter(ch => !searchQuery || ch.title.toLowerCase().includes(searchQuery.toLowerCase()))
                .map((ch) => (
                  <div
                    key={ch.id}
                    onClick={() => {
                      if (!userProfile) {
                        setShowRegisterModal(true);
                        return;
                      }
                      setCurrentChapterIndex(ch.originalIdx);
                      setActiveTab('reader');
                    }}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      padding: '16px',
                      background: ch.originalIdx === currentChapterIndex ? 'var(--accent-light)' : 'var(--bg-surface)',
                      border: `1px solid ${ch.originalIdx === currentChapterIndex ? 'var(--accent)' : 'var(--border)'}`,
                      borderRadius: '14px',
                      cursor: 'pointer',
                      transition: 'all 0.15s ease'
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
                      <span style={{
                        width: '32px',
                        height: '32px',
                        borderRadius: '50%',
                        background: ch.originalIdx === currentChapterIndex ? 'var(--accent)' : 'var(--bg-card)',
                        color: ch.originalIdx === currentChapterIndex ? '#fff' : 'var(--text-muted)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontSize: '14px',
                        fontWeight: 600,
                        fontFamily: 'var(--font-sans)'
                      }}>
                        {toBnNum(ch.originalIdx + 1)}
                      </span>
                      <div>
                        <div style={{
                          fontSize: '15px',
                          fontWeight: ch.originalIdx === currentChapterIndex ? 600 : 500,
                          color: 'var(--text-primary)'
                        }}>
                          {ch.title}
                        </div>
                        <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '2px', fontFamily: 'var(--font-sans)' }}>
                          পৃষ্ঠা {toBnNum(ch.startPage)} - {toBnNum(ch.endPage)} • {toBnNum(ch.readTimeMinutes)} মিনিট পাঠ
                        </div>
                      </div>
                    </div>

                    <ChevronRight size={18} color="var(--text-muted)" />
                  </div>
                ))}
            </div>
          </div>
        )}

        {/* TAB 4: PROFILE & SETTINGS */}
        {activeTab === 'profile' && (
          <div style={{ padding: '24px 20px' }}>
            {/* User Account Card */}
            <div style={{
              background: 'var(--bg-surface)',
              borderRadius: '20px',
              padding: '24px 20px',
              border: '1px solid var(--border)',
              marginBottom: '24px',
              boxShadow: 'var(--shadow)'
            }}>
              {userProfile ? (
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '14px', marginBottom: '16px' }}>
                    <div style={{
                      width: '54px',
                      height: '54px',
                      borderRadius: '50%',
                      background: 'var(--accent)',
                      color: '#ffffff',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: '22px',
                      fontWeight: 700
                    }}>
                      {userProfile.name ? userProfile.name.charAt(0).toUpperCase() : 'U'}
                    </div>
                    <div>
                      <h3 style={{ fontSize: '18px', fontWeight: 600 }}>{userProfile.name}</h3>
                      <p style={{ fontSize: '13px', color: 'var(--text-muted)' }}>{userProfile.email}</p>
                    </div>
                  </div>
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px',
                    fontSize: '12px',
                    color: '#10b981',
                    background: 'rgba(16, 185, 129, 0.1)',
                    padding: '8px 12px',
                    borderRadius: '8px'
                  }}>
                    <CheckCircle size={14} />
                    <span>বিনামূল্যে সম্পূর্ণ পাঠাগার এক্সেস সক্রিয় রয়েছে</span>
                  </div>
                </div>
              ) : (
                <div style={{ textAlign: 'center', padding: '10px 0' }}>
                  <div style={{
                    width: '60px',
                    height: '60px',
                    borderRadius: '50%',
                    background: 'var(--bg-card)',
                    color: 'var(--text-muted)',
                    display: 'inline-flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    marginBottom: '12px'
                  }}>
                    <User size={28} />
                  </div>
                  <h3 style={{ fontSize: '18px', fontWeight: 600, marginBottom: '6px' }}>
                    পাঠক প্রোফাইল তৈরি করুন
                  </h3>
                  <p style={{ fontSize: '14px', color: 'var(--text-secondary)', marginBottom: '18px' }}>
                    বুকমার্ক সংরক্ষণ ও অফলাইন রিডিং পারসোনালাইজ করতে সাইন-আপ করুন।
                  </p>
                  <button 
                    className="primary-btn" 
                    style={{ width: '100%' }}
                    onClick={() => setShowRegisterModal(true)}
                  >
                    ফ্রি সাইন-আপ করুন
                  </button>
                </div>
              )}
            </div>

            {/* Reading Stats Card */}
            <div style={{
              background: 'var(--bg-surface)',
              borderRadius: '20px',
              padding: '20px',
              border: '1px solid var(--border)',
              marginBottom: '24px'
            }}>
              <h4 style={{ fontSize: '15px', fontWeight: 600, marginBottom: '14px' }}>
                আপনার পড়ার অগ্রগতি
              </h4>
              <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                fontSize: '14px',
                color: 'var(--text-secondary)',
                marginBottom: '8px',
                fontFamily: 'var(--font-sans)'
              }}>
                <span>বর্তমান অধ্যায়</span>
                <span style={{ fontWeight: 600, color: 'var(--text-primary)' }}>
                  {toBnNum(currentChapterIndex + 1)} / {toBnNum(bookData.chapters.length)}
                </span>
              </div>
              <div style={{
                height: '8px',
                background: 'var(--bg-card)',
                borderRadius: '8px',
                overflow: 'hidden'
              }}>
                <div style={{
                  height: '100%',
                  width: `${Math.round(((currentChapterIndex + 1) / bookData.chapters.length) * 100)}%`,
                  background: 'var(--accent)',
                  borderRadius: '8px'
                }} />
              </div>
            </div>

            {/* About Iqra Research */}
            <div style={{
              background: 'var(--bg-surface)',
              borderRadius: '20px',
              padding: '20px',
              border: '1px solid var(--border)',
              fontSize: '13px',
              color: 'var(--text-secondary)',
              lineHeight: 1.7
            }}>
              <h4 style={{ fontSize: '15px', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '8px' }}>
                প্রকাশনা পরিচিতি
              </h4>
              <p>
                <strong>ইক্বরা (IQRA)</strong> - দি ইন্সটিটিউট অব কুরআনিক রিসার্চ এন্ড এ্যাপ্লিকেশন। কুরআন ভিত্তিক মৌলিক চিন্তন, সংস্কার ও প্রামাণ্য গবেষণার প্রসারে নিবেদিত প্রতিষ্ঠান।
              </p>
            </div>
          </div>
        )}
      </main>

      {/* Reader Font & Theme Bottom Sheet */}
      {showSettingsSheet && (
        <>
          <div className="bottom-sheet-backdrop" onClick={() => setShowSettingsSheet(false)} />
          <div className="bottom-sheet">
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginBottom: '20px'
            }}>
              <h3 style={{ fontSize: '17px', fontWeight: 600 }}>পড়ার থিম ও ফন্ট সেটিংস</h3>
              <button 
                className="icon-btn" 
                onClick={() => setShowSettingsSheet(false)}
              >
                <X size={18} />
              </button>
            </div>

            {/* Color Theme Selector */}
            <div style={{ marginBottom: '22px' }}>
              <div style={{ fontSize: '13px', color: 'var(--text-muted)', marginBottom: '10px' }}>
                কালার থিম
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '8px' }}>
                {[
                  { id: 'sepia', label: 'ওয়ার্ম', bg: '#fbf0d9', text: '#433422' },
                  { id: 'light', label: 'লাইট', bg: '#ffffff', text: '#0f172a' },
                  { id: 'midnight', label: 'মিডনাইট', bg: '#0b1120', text: '#f1f5f9' },
                  { id: 'dark', label: 'ডার্ক', bg: '#000000', text: '#f1f5f9' }
                ].map(t => (
                  <button
                    key={t.id}
                    onClick={() => setTheme(t.id)}
                    style={{
                      background: t.bg,
                      color: t.text,
                      border: theme === t.id ? '2px solid var(--accent)' : '1px solid rgba(120,120,120,0.2)',
                      padding: '12px 6px',
                      borderRadius: '12px',
                      fontSize: '13px',
                      fontWeight: 600,
                      cursor: 'pointer',
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: 'center',
                      gap: '4px'
                    }}
                  >
                    <span>{t.label}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Font Size Selector */}
            <div style={{ marginBottom: '22px' }}>
              <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                fontSize: '13px',
                color: 'var(--text-muted)',
                marginBottom: '10px'
              }}>
                <span>ফন্টের সাইজ</span>
                <span>{fontSize}px</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <button 
                  className="icon-btn" 
                  style={{ flex: 1, borderRadius: '12px', height: '42px', fontSize: '14px', fontWeight: 700 }}
                  onClick={() => setFontSize(prev => Math.max(15, prev - 1))}
                >
                  A-
                </button>
                <button 
                  className="icon-btn" 
                  style={{ flex: 1, borderRadius: '12px', height: '42px', fontSize: '18px', fontWeight: 700 }}
                  onClick={() => setFontSize(prev => Math.min(28, prev + 1))}
                >
                  A+
                </button>
              </div>
            </div>

            {/* Font Family Selector */}
            <div>
              <div style={{ fontSize: '13px', color: 'var(--text-muted)', marginBottom: '10px' }}>
                ফন্ট স্টাইল
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                <button
                  onClick={() => setFontFamily('serif')}
                  style={{
                    padding: '12px',
                    borderRadius: '12px',
                    border: fontFamily === 'serif' ? '2px solid var(--accent)' : '1px solid var(--border)',
                    background: 'var(--bg-card)',
                    color: 'var(--text-primary)',
                    fontFamily: 'var(--font-serif)',
                    fontSize: '15px',
                    cursor: 'pointer'
                  }}
                >
                  সেরিফ (বইয়ের মতো)
                </button>
                <button
                  onClick={() => setFontFamily('sans')}
                  style={{
                    padding: '12px',
                    borderRadius: '12px',
                    border: fontFamily === 'sans' ? '2px solid var(--accent)' : '1px solid var(--border)',
                    background: 'var(--bg-card)',
                    color: 'var(--text-primary)',
                    fontFamily: 'var(--font-sans)',
                    fontSize: '15px',
                    cursor: 'pointer'
                  }}
                >
                  স্যান্স (ক্লিন আধুনিক)
                </button>
              </div>
            </div>
          </div>
        </>
      )}

      {/* Free Registration Modal */}
      {showRegisterModal && (
        <>
          <div className="bottom-sheet-backdrop" onClick={() => setShowRegisterModal(false)} />
          <div className="bottom-sheet">
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginBottom: '16px'
            }}>
              <div>
                <h3 style={{ fontSize: '18px', fontWeight: 600 }}>বইটি পড়ার জন্য সাইন-আপ করুন</h3>
                <p style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '2px' }}>
                  একবার তথ্য জমা দিলে সম্পূর্ণ বইটি বিনামূল্যে পড়তে পারবেন
                </p>
              </div>
              <button className="icon-btn" onClick={() => setShowRegisterModal(false)}>
                <X size={18} />
              </button>
            </div>

            {formError && (
              <div style={{
                background: '#fee2e2',
                color: '#b91c1c',
                padding: '10px 14px',
                borderRadius: '10px',
                fontSize: '13px',
                marginBottom: '12px'
              }}>
                {formError}
              </div>
            )}

            <form onSubmit={handleRegister} style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <div>
                <label style={{ display: 'block', fontSize: '13px', marginBottom: '5px', color: 'var(--text-secondary)' }}>
                  আপনার পূর্ণ নাম (Name) *
                </label>
                <input
                  name="name"
                  required
                  placeholder="যেমন: সাদিক আলম"
                  style={{
                    width: '100%',
                    padding: '11px 14px',
                    borderRadius: '12px',
                    border: '1px solid var(--border)',
                    background: 'var(--bg-card)',
                    color: 'var(--text-primary)',
                    fontFamily: 'var(--font-sans)',
                    fontSize: '15px',
                    outline: 'none'
                  }}
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '13px', marginBottom: '5px', color: 'var(--text-secondary)' }}>
                  হোয়াটসঅ্যাপ নম্বর (WhatsApp) *
                </label>
                <input
                  name="whatsapp"
                  type="tel"
                  required
                  placeholder="017XXXXXXXX"
                  style={{
                    width: '100%',
                    padding: '11px 14px',
                    borderRadius: '12px',
                    border: '1px solid var(--border)',
                    background: 'var(--bg-card)',
                    color: 'var(--text-primary)',
                    fontFamily: 'var(--font-sans)',
                    fontSize: '15px',
                    outline: 'none'
                  }}
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '13px', marginBottom: '5px', color: 'var(--text-secondary)' }}>
                  ইমেইল (Email) *
                </label>
                <input
                  name="email"
                  type="email"
                  required
                  placeholder="name@example.com"
                  style={{
                    width: '100%',
                    padding: '11px 14px',
                    borderRadius: '12px',
                    border: '1px solid var(--border)',
                    background: 'var(--bg-card)',
                    color: 'var(--text-primary)',
                    fontFamily: 'var(--font-sans)',
                    fontSize: '15px',
                    outline: 'none'
                  }}
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '13px', marginBottom: '5px', color: 'var(--text-secondary)' }}>
                  শহর / জেলা (City) *
                </label>
                <input
                  name="city"
                  required
                  placeholder="যেমন: ঢাকা / চট্টগ্রাম"
                  style={{
                    width: '100%',
                    padding: '11px 14px',
                    borderRadius: '12px',
                    border: '1px solid var(--border)',
                    background: 'var(--bg-card)',
                    color: 'var(--text-primary)',
                    fontFamily: 'var(--font-sans)',
                    fontSize: '15px',
                    outline: 'none'
                  }}
                />
              </div>

              <button 
                type="submit" 
                className="primary-btn" 
                disabled={isSubmitting}
                style={{ width: '100%', padding: '14px', marginTop: '6px', opacity: isSubmitting ? 0.7 : 1 }}
              >
                {isSubmitting ? 'সংরক্ষণ করা হচ্ছে...' : 'জমা দিন ও পড়া শুরু করুন'}
              </button>
            </form>
          </div>
        </>
      )}

      {/* Translucent Bottom Navigation Bar */}
      <nav className="bottom-nav">
        <button 
          className={`nav-item ${activeTab === 'home' ? 'active' : ''}`}
          onClick={() => setActiveTab('home')}
        >
          <HomeIcon />
          <span>হোম</span>
        </button>

        <button 
          className={`nav-item ${activeTab === 'reader' ? 'active' : ''}`}
          onClick={handleStartReading}
        >
          <BookOpen />
          <span>পড়ুন</span>
        </button>

        <button 
          className={`nav-item ${activeTab === 'toc' ? 'active' : ''}`}
          onClick={() => {
            if (userProfile) {
              setActiveTab('toc');
            } else {
              setShowRegisterModal(true);
            }
          }}
        >
          <List />
          <span>সূচিপত্র</span>
        </button>

        <button 
          className={`nav-item ${activeTab === 'profile' ? 'active' : ''}`}
          onClick={() => setActiveTab('profile')}
        >
          <User />
          <span>প্রোফাইল</span>
        </button>
      </nav>
    </div>
  );
}
