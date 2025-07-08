import { useState, useEffect } from "react";
import {
  Video,
  Car,
  Bike,
  Gauge,
  AlertCircle,
  CheckCircle,
  Clock,
} from "lucide-react";

export default function VideoCard({ videoName, info, onClick, isFocused }) {
  const [windowWidth, setWindowWidth] = useState(window.innerWidth);
  const [currentFrame, setCurrentFrame] = useState(null);

  useEffect(() => {
    const handleResize = () => {
      setWindowWidth(window.innerWidth);
    };

    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  // Update frame with smooth transition
  useEffect(() => {
    if (info.frame && info.frame !== currentFrame) {
      // Add a small delay to prevent rapid flickering
      const timer = setTimeout(() => {
        setCurrentFrame(info.frame);
      }, 50);

      return () => clearTimeout(timer);
    }
  }, [info.frame, currentFrame]);
  const getStatusColor = () => {
    const totalVehicles = (info.count_car || 0) + (info.count_motor || 0);
    if (totalVehicles > 15) return "#ef4444";
    if (totalVehicles > 8) return "#f59e0b";
    return "#10b981";
  };

  const getStatusIcon = () => {
    const totalVehicles = (info.count_car || 0) + (info.count_motor || 0);
    if (totalVehicles > 15) return <AlertCircle size={16} />;
    if (totalVehicles > 8) return <Clock size={16} />;
    return <CheckCircle size={16} />;
  };

  // Responsive styles based on screen size
  const getResponsiveStyles = () => {
    const baseStyles = {
      background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
      borderRadius: 28,
      cursor: "pointer",
      transform: isFocused ? "scale(1.08)" : "scale(1)",
      transition: "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
      boxShadow: isFocused
        ? "0 24px 48px rgba(102, 126, 234, 0.4), 0 0 0 3px #667eea"
        : "0 12px 32px rgba(0, 0, 0, 0.14)",
      color: "white",
      position: "relative",
      overflow: "hidden",
    };

    // Check if we're on desktop (width > 768px)
    const isDesktop = windowWidth > 768;

    if (isDesktop) {
      return {
        ...baseStyles,
        padding: 32,
        minWidth: "70vw",
        maxWidth: "70vw",
        minHeight: 500,
        display: "flex",
        gap: 32,
      };
    } else {
      return {
        ...baseStyles,
        padding: 24,
        minWidth: 320,
        maxWidth: 400,
        minHeight: 380,
        display: "block",
      };
    }
  };

  const isDesktop = windowWidth > 768;

  return (
    <div onClick={onClick} style={getResponsiveStyles()}>
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background:
            "linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0) 100%)",
          pointerEvents: "none",
        }}
      />

      {/* Desktop Layout: Video Left, Info Right */}
      {isDesktop ? (
        <>
          {/* Video Section - Left Side */}
          <div
            style={{
              flex: "1.2",
              display: "flex",
              flexDirection: "column",
            }}
          >
            <div
              style={{
                borderRadius: 16,
                overflow: "hidden",
                border: "2px solid rgba(255, 255, 255, 0.2)",
                height: "100%",
                minHeight: "400px",
                position: "relative",
                backgroundColor: "rgba(0, 0, 0, 0.2)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              {currentFrame ? (
                <img
                  key={currentFrame} // Force re-render with new key
                  src={`data:image/jpeg;base64,${currentFrame}`}
                  alt="Video frame"
                  style={{
                    width: "100%",
                    height: "100%",
                    display: "block",
                    objectFit: "cover",
                    transition: "opacity 0.15s ease-in-out",
                  }}
                />
              ) : (
                <div
                  style={{
                    color: "rgba(255, 255, 255, 0.6)",
                    fontSize: 18,
                    display: "flex",
                    alignItems: "center",
                    gap: 8,
                  }}
                >
                  <Video size={24} />
                  <span>Loading video...</span>
                </div>
              )}
            </div>
          </div>

          {/* Information Section - Right Side */}
          <div
            style={{
              flex: "1",
              display: "flex",
              flexDirection: "column",
              gap: 24,
            }}
          >
            {/* Header */}
            <div
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                flexWrap: "wrap",
                gap: 16,
              }}
            >
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 12,
                }}
              >
                <Video size={32} />
                <h3
                  style={{
                    fontSize: 28,
                    fontWeight: 700,
                    margin: 0,
                    textShadow: "0 2px 4px rgba(0,0,0,0.3)",
                  }}
                >
                  {videoName}
                </h3>
              </div>
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 6,
                  background: getStatusColor(),
                  padding: "8px 16px",
                  borderRadius: 16,
                  fontSize: 16,
                  fontWeight: 600,
                }}
              >
                {getStatusIcon()}
                <span>
                  {(info.count_car || 0) + (info.count_motor || 0) > 15
                    ? "Tắc"
                    : (info.count_car || 0) + (info.count_motor || 0) > 8
                    ? "Đông"
                    : "Thông"}
                </span>
              </div>
            </div>

            {/* Vehicle Statistics */}
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "1fr 1fr",
                gap: 20,
              }}
            >
              <div
                style={{
                  background: "rgba(255, 255, 255, 0.15)",
                  padding: 24,
                  borderRadius: 16,
                  backdropFilter: "blur(10px)",
                }}
              >
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: 12,
                    marginBottom: 16,
                  }}
                >
                  <Car size={24} />
                  <span style={{ fontSize: 18, fontWeight: 600 }}>Ô tô</span>
                </div>
                <div style={{ fontSize: 36, fontWeight: 800, marginBottom: 8 }}>
                  {info.count_car || 0}
                </div>
                <div style={{ fontSize: 16, opacity: 0.8 }}>
                  {info.speed_car || 0} km/h
                </div>
              </div>

              <div
                style={{
                  background: "rgba(255, 255, 255, 0.15)",
                  padding: 24,
                  borderRadius: 16,
                  backdropFilter: "blur(10px)",
                }}
              >
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: 12,
                    marginBottom: 16,
                  }}
                >
                  <Bike size={24} />
                  <span style={{ fontSize: 18, fontWeight: 600 }}>Xe máy</span>
                </div>
                <div style={{ fontSize: 36, fontWeight: 800, marginBottom: 8 }}>
                  {info.count_motor || 0}
                </div>
                <div style={{ fontSize: 16, opacity: 0.8 }}>
                  {info.speed_motor || 0} km/h
                </div>
              </div>
            </div>

            {/* Total Vehicles */}
            <div
              style={{
                background: "rgba(255, 255, 255, 0.15)",
                padding: 24,
                borderRadius: 16,
                backdropFilter: "blur(10px)",
                display: "flex",
                alignItems: "center",
                gap: 16,
              }}
            >
              <Gauge size={24} />
              <span style={{ fontSize: 18, fontWeight: 600 }}>
                Tổng phương tiện:{" "}
                {(info.count_car || 0) + (info.count_motor || 0)}
              </span>
            </div>
          </div>
        </>
      ) : (
        /* Mobile Layout: Original Vertical Layout */
        <>
          {/* Hiển thị frame nếu có */}
          <div
            style={{
              marginBottom: 16,
              borderRadius: 12,
              overflow: "hidden",
              border: "2px solid rgba(255, 255, 255, 0.2)",
              height: "200px",
              position: "relative",
              backgroundColor: "rgba(0, 0, 0, 0.2)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            {currentFrame ? (
              <img
                key={currentFrame} // Force re-render with new key
                src={`data:image/jpeg;base64,${currentFrame}`}
                alt="Video frame"
                style={{
                  width: "100%",
                  height: "100%",
                  display: "block",
                  objectFit: "cover",
                  transition: "opacity 0.15s ease-in-out",
                }}
              />
            ) : (
              <div
                style={{
                  color: "rgba(255, 255, 255, 0.6)",
                  fontSize: 14,
                  display: "flex",
                  alignItems: "center",
                  gap: 6,
                }}
              >
                <Video size={16} />
                <span>Loading...</span>
              </div>
            )}
          </div>

          {/* Mobile Header */}
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              marginBottom: 16,
            }}
          >
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: 8,
              }}
            >
              <Video size={20} />
              <h3
                style={{
                  fontSize: 18,
                  fontWeight: 700,
                  margin: 0,
                  textShadow: "0 2px 4px rgba(0,0,0,0.3)",
                }}
              >
                {videoName}
              </h3>
            </div>
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: 4,
                background: getStatusColor(),
                padding: "4px 8px",
                borderRadius: 12,
                fontSize: 12,
                fontWeight: 600,
              }}
            >
              {getStatusIcon()}
              <span>
                {(info.count_car || 0) + (info.count_motor || 0) > 15
                  ? "Tắc"
                  : (info.count_car || 0) + (info.count_motor || 0) > 8
                  ? "Đông"
                  : "Thông"}
              </span>
            </div>
          </div>

          {/* Mobile Vehicle Statistics */}
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "1fr 1fr",
              gap: 16,
              marginBottom: 16,
            }}
          >
            <div
              style={{
                background: "rgba(255, 255, 255, 0.15)",
                padding: 12,
                borderRadius: 12,
                backdropFilter: "blur(10px)",
              }}
            >
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 8,
                  marginBottom: 8,
                }}
              >
                <Car size={16} />
                <span style={{ fontSize: 14, fontWeight: 600 }}>Ô tô</span>
              </div>
              <div style={{ fontSize: 20, fontWeight: 800 }}>
                {info.count_car || 0}
              </div>
              <div style={{ fontSize: 12, opacity: 0.8 }}>
                {info.speed_car || 0} km/h
              </div>
            </div>

            <div
              style={{
                background: "rgba(255, 255, 255, 0.15)",
                padding: 12,
                borderRadius: 12,
                backdropFilter: "blur(10px)",
              }}
            >
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 8,
                  marginBottom: 8,
                }}
              >
                <Bike size={16} />
                <span style={{ fontSize: 14, fontWeight: 600 }}>Xe máy</span>
              </div>
              <div style={{ fontSize: 20, fontWeight: 800 }}>
                {info.count_motor || 0}
              </div>
              <div style={{ fontSize: 12, opacity: 0.8 }}>
                {info.speed_motor || 0} km/h
              </div>
            </div>
          </div>

          {/* Mobile Total Vehicles */}
          <div
            style={{
              background: "rgba(255, 255, 255, 0.15)",
              padding: 12,
              borderRadius: 12,
              backdropFilter: "blur(10px)",
              display: "flex",
              alignItems: "center",
              gap: 8,
            }}
          >
            <Gauge size={16} />
            <span style={{ fontSize: 14, fontWeight: 600 }}>
              Tổng phương tiện:{" "}
              {(info.count_car || 0) + (info.count_motor || 0)}
            </span>
          </div>
        </>
      )}
    </div>
  );
}
