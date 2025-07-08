import React, { useState, useEffect } from "react";
import VideoCard from "./VideoCard";
import { ChevronLeft, ChevronRight } from "lucide-react";

// Only show the specified roads - moved outside component to avoid dependency issues
const ALLOWED_ROADS = [
  "Văn Phú",
  "Nguyễn Trãi",
  "Ngã Tư Sở",
  "Đường Láng",
  "Văn Quán",
];

export default function VideoCarousel({ focused, setFocused }) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [framesData, setFramesData] = useState(null);
  const [vehiclesData, setVehiclesData] = useState(null);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  const currentRoad = ALLOWED_ROADS[currentIndex];

  // Fetch frames every 200ms for all roads
  useEffect(() => {
    let timer;
    const fetchFrames = async () => {
      try {
        const res = await fetch("http://localhost:8000/frames");
        const frames = await res.json();
        // Keep data for all roads, but filter to only allowed roads
        const filteredFrames = {};
        ALLOWED_ROADS.forEach((road) => {
          if (frames[road]) {
            filteredFrames[road] = frames[road];
          }
        });
        setFramesData(filteredFrames);
      } catch (e) {
        setFramesData(null);
      }
      timer = setTimeout(fetchFrames, 200);
    };
    fetchFrames();
    return () => clearTimeout(timer);
  }, []); // Remove currentRoad dependency since we're fetching all roads

  // Fetch vehicles every 4000ms for all roads
  useEffect(() => {
    let timer;
    const fetchVehicles = async () => {
      try {
        const res = await fetch("http://localhost:8000/veheicles");
        const vehicles = await res.json();
        // Keep data for all roads, but filter to only allowed roads
        const filteredVehicles = {};
        ALLOWED_ROADS.forEach((road) => {
          if (vehicles[road]) {
            filteredVehicles[road] = vehicles[road];
          }
        });
        setVehiclesData(filteredVehicles);
      } catch (e) {
        setVehiclesData(null);
      }
      timer = setTimeout(fetchVehicles, 4000);
    };
    fetchVehicles();
    return () => clearTimeout(timer);
  }, []); // Remove currentRoad dependency since we're fetching all roads

  // Merge data when either framesData or vehiclesData changes
  useEffect(() => {
    if (!framesData && !vehiclesData) {
      setData(null);
      setLoading(true);
      return;
    }
    const merged = {};

    // Merge data for all roads
    ALLOWED_ROADS.forEach((road) => {
      merged[road] = {};

      if (framesData && framesData[road]) {
        merged[road] = {
          ...merged[road],
          ...framesData[road],
        };
      }

      if (vehiclesData && vehiclesData[road]) {
        merged[road] = {
          ...merged[road],
          ...vehiclesData[road],
        };
      }
    });

    setData(merged);
    setLoading(false);
  }, [framesData, vehiclesData]);

  const nextVideo = () => {
    setCurrentIndex((prev) => (prev + 1) % ALLOWED_ROADS.length);
  };

  const prevVideo = () => {
    setCurrentIndex(
      (prev) => (prev - 1 + ALLOWED_ROADS.length) % ALLOWED_ROADS.length
    );
  };

  if (loading) {
    return (
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          minHeight: 400,
          gap: 16,
        }}
      >
        <div
          style={{
            width: 60,
            height: 60,
            border: "4px solid #e2e8f0",
            borderTop: "4px solid #667eea",
            borderRadius: "50%",
            animation: "spin 1s linear infinite",
          }}
        />
        <div
          style={{
            fontSize: 18,
            color: "#64748b",
            fontWeight: 600,
          }}
        >
          Đang tải dữ liệu giám sát...
        </div>
      </div>
    );
  }

  const carouselStyle = {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    width: "100%",
    padding: "32px 0",
    gap: 24,
    maxWidth: "100%",
    overflow: "hidden",
  };

  const videoContainerStyle = {
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    gap: 24,
    width: "100%",
  };

  const navigationButtonStyle = {
    background: "rgba(255, 255, 255, 0.2)",
    border: "none",
    borderRadius: "50%",
    width: 48,
    height: 48,
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    cursor: "pointer",
    color: "white",
    transition: "all 0.3s ease",
    backdropFilter: "blur(10px)",
  };

  const indicatorContainerStyle = {
    display: "flex",
    gap: 8,
    alignItems: "center",
  };

  const indicatorStyle = (isActive) => ({
    width: isActive ? 24 : 8,
    height: 8,
    borderRadius: 4,
    background: isActive ? "white" : "rgba(255, 255, 255, 0.4)",
    transition: "all 0.3s ease",
    cursor: "pointer",
  });

  const currentVideoData = data && data[currentRoad] ? data[currentRoad] : {};

  return (
    <div style={carouselStyle}>
      <div style={videoContainerStyle}>
        <button
          style={navigationButtonStyle}
          onClick={prevVideo}
          onMouseEnter={(e) => {
            e.target.style.background = "rgba(255, 255, 255, 0.3)";
            e.target.style.transform = "scale(1.1)";
          }}
          onMouseLeave={(e) => {
            e.target.style.background = "rgba(255, 255, 255, 0.2)";
            e.target.style.transform = "scale(1)";
          }}
        >
          <ChevronLeft size={24} />
        </button>

        <VideoCard
          key={currentRoad}
          videoName={currentRoad}
          info={currentVideoData}
          onClick={() => setFocused(currentRoad)}
          isFocused={focused === currentRoad}
        />

        <button
          style={navigationButtonStyle}
          onClick={nextVideo}
          onMouseEnter={(e) => {
            e.target.style.background = "rgba(255, 255, 255, 0.3)";
            e.target.style.transform = "scale(1.1)";
          }}
          onMouseLeave={(e) => {
            e.target.style.background = "rgba(255, 255, 255, 0.2)";
            e.target.style.transform = "scale(1)";
          }}
        >
          <ChevronRight size={24} />
        </button>
      </div>

      <div style={indicatorContainerStyle}>
        {ALLOWED_ROADS.map((road, index) => (
          <div
            key={road}
            style={indicatorStyle(index === currentIndex)}
            onClick={() => setCurrentIndex(index)}
          />
        ))}
      </div>

      <div
        style={{
          fontSize: 16,
          color: "rgba(255, 255, 255, 0.8)",
          fontWeight: 600,
          textAlign: "center",
        }}
      >
        {currentIndex + 1} / {ALLOWED_ROADS.length} - {currentRoad}
      </div>
    </div>
  );
}
