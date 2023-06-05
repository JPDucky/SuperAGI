import React, {useEffect, useRef, useState} from 'react';
import styles from './Agents.module.css';
import Head from 'next/head';
import {getExecutionFeeds} from "@/pages/api/DashboardService";
import Image from "next/image";
import {formatTime} from "@/utils/utils";

export default function ActivityFeed({selectedRunId}) {
  const [loadingText, setLoadingText] = useState("Thinking");
  const [feeds, setFeeds] = useState([]);
  const feedContainerRef = useRef(null);
  const [runStatus, setRunStatus] = useState("CREATED");
  const [prevFeedsLength, setPrevFeedsLength] = useState(0);

  useEffect(() => {
    const text = 'Thinking';
    let dots = '';

    const interval = setInterval(() => {
      dots = dots.length < 3 ? dots + '.' : '';
      setLoadingText(`${text}${dots}`);
    }, 250);

    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const interval = window.setInterval(function(){
      fetchFeeds();
    }, 10000);

    return () => clearInterval(interval);
  }, [selectedRunId]);

  useEffect(() => {
    if (feeds.length !== prevFeedsLength) {
      if (feedContainerRef.current) {
        setTimeout(() => {
          feedContainerRef.current.scrollTo({ top: feedContainerRef.current.scrollHeight, behavior: 'smooth' });
          setPrevFeedsLength(feeds.length);
        }, 100);
      }
    }
  }, [feeds]);

  useEffect(() => {
    fetchFeeds();
  }, [selectedRunId])

  function fetchFeeds() {
    getExecutionFeeds(selectedRunId)
      .then((response) => {
        const feedsArray = response.data;
        setFeeds(feedsArray);
        setRunStatus(feedsArray[feedsArray.length - 1].status);
      })
      .catch((error) => {
        console.error('Error fetching execution feeds:', error);
      });
  }

  return (<>
    <Head>
      {/* eslint-disable-next-line @next/next/no-page-custom-font */}
      <link href="https://fonts.googleapis.com/css2?family=Source+Code+Pro&display=swap" rel="stylesheet"/>
    </Head>
    <div style={{overflowY: "auto",maxHeight:'80vh'}} ref={feedContainerRef}>
      <div style={{marginBottom:'140px'}} ref={feedContainerRef}>
        {feeds && feeds.map((f, index) => (<div key={index} className={styles.history_box} style={{background:'#272335',padding:'20px',cursor:'default'}}>
          <div style={{display:'flex'}}>
            {f.role === 'user' && <div className={styles.feed_icon}>💁</div>}
            {f.role === 'system' && <div className={styles.feed_icon}>🛠️ </div>}
            {f.role === 'assistant' && <div className={styles.feed_icon}>💡</div>}
            <div className={styles.feed_title}>{f?.feed || ''}</div>
          </div>
          <div className={styles.more_details_wrapper}>
            {f.updated_at && formatTime(f.updated_at) !== 'Invalid Time' && <div className={styles.more_details}>
              <div style={{display: 'flex', alignItems: 'center'}}>
                <div>
                  <Image width={12} height={12} src="/images/schedule.svg" alt="schedule-icon"/>
                </div>
                <div className={styles.history_info}>
                  {formatTime(f.updated_at)}
                </div>
              </div>
            </div>}
          </div>
        </div>))}
        {runStatus === 'RUNNING' && <div className={styles.history_box} style={{background: '#272335', padding: '20px', cursor: 'default'}}>
          <div style={{display: 'flex'}}>
            <div style={{fontSize: '20px'}}>🧠</div>
            <div className={styles.feed_title}><i>{loadingText}</i></div>
          </div>
        </div>}
        {runStatus === 'COMPLETED' && <div className={styles.history_box} style={{background: '#272335', padding: '20px', cursor: 'default'}}>
          <div style={{display: 'flex'}}>
            <div style={{fontSize: '20px'}}>🏁</div>
            <div className={styles.feed_title}><i>All goals completed successfully!</i></div>
          </div>
        </div>}
      </div>
    </div>
  </>)
}