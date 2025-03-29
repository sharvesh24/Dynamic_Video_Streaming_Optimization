import tkinter as tk
from tkinter import ttk
import threading
import time
import random
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class AdaptiveVideoStreaming:
    def _init_(self, root):
        self.root = root
        self.root.title("Adaptive Video Streaming Simulation")
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f0f0")
        
        # Stream parameters
        self.is_streaming = False
        self.network_speed = 5.0  # Mbps
        self.buffer_size = 0      # seconds
        self.current_quality = 2  # Index of quality level
        self.quality_levels = [
            {"name": "240p", "bitrate": 1.0},
            {"name": "360p", "bitrate": 2.0},
            {"name": "480p", "bitrate": 3.0},
            {"name": "720p", "bitrate": 5.0},
            {"name": "1080p", "bitrate": 8.0},
            {"name": "4K", "bitrate": 16.0}
        ]
        self.chunk_size = 2  # seconds
        self.buffer_history = []
        self.quality_history = []
        self.network_history = []
        self.target_buffer = 10  # seconds
        
        # Create UI elements
        self.create_ui()
        
        # Update UI
        self.update_ui()
    
    def create_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Control panel
        control_frame = ttk.LabelFrame(main_frame, text="Streaming Controls", padding=10)
        control_frame.pack(fill=tk.X, pady=10)
        
        # Start/Stop button
        self.stream_button = ttk.Button(control_frame, text="Start Streaming", command=self.toggle_streaming)
        self.stream_button.pack(side=tk.LEFT, padx=5)
        
        # Network speed slider
        ttk.Label(control_frame, text="Network Speed (Mbps):").pack(side=tk.LEFT, padx=(20, 5))
        self.network_slider = ttk.Scale(control_frame, from_=0.5, to=20.0, orient=tk.HORIZONTAL, 
                                       length=200, value=self.network_speed, command=self.update_network_speed)
        self.network_slider.pack(side=tk.LEFT, padx=5)
        self.network_value_label = ttk.Label(control_frame, text=f"{self.network_speed:.1f}")
        self.network_value_label.pack(side=tk.LEFT, padx=5)
        
        # Network fluctuation
        self.network_fluctuation_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(control_frame, text="Network Fluctuation", variable=self.network_fluctuation_var).pack(side=tk.LEFT, padx=20)
        
        # Status frame
        status_frame = ttk.LabelFrame(main_frame, text="Streaming Status", padding=10)
        status_frame.pack(fill=tk.X, pady=10)
        
        # Status grid
        status_grid = ttk.Frame(status_frame)
        status_grid.pack(fill=tk.X)
        
        # Current quality
        ttk.Label(status_grid, text="Current Quality:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.quality_label = ttk.Label(status_grid, text="480p")
        self.quality_label.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Buffer size
        ttk.Label(status_grid, text="Buffer Size:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.buffer_label = ttk.Label(status_grid, text="0 seconds")
        self.buffer_label.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Buffer progress bar
        ttk.Label(status_grid, text="Buffer:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.buffer_progress = ttk.Progressbar(status_grid, orient=tk.HORIZONTAL, length=200, mode='determinate')
        self.buffer_progress.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Chunk processing
        ttk.Label(status_grid, text="Chunk Processing:").grid(row=0, column=2, sticky=tk.W, padx=(30, 5), pady=5)
        self.chunk_frame = ttk.Frame(status_grid)
        self.chunk_frame.grid(row=0, column=3, rowspan=3, sticky=tk.W, padx=5, pady=5)
        
        self.chunk_labels = []
        for i in range(5):
            chunk = ttk.Label(self.chunk_frame, text="□", font=("Arial", 16))
            chunk.pack(side=tk.LEFT, padx=2)
            self.chunk_labels.append(chunk)
        
        # Video display area
        video_frame = ttk.LabelFrame(main_frame, text="Video Preview", padding=10)
        video_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Placeholder for video (using a canvas)
        self.video_canvas = tk.Canvas(video_frame, bg="black", width=640, height=360)
        self.video_canvas.pack(padx=10, pady=10)
        
        # Text representing the video quality
        self.video_quality_text = self.video_canvas.create_text(
            320, 180, text="480p", fill="white", font=("Arial", 36)
        )
        
        # Create graphs
        graph_frame = ttk.LabelFrame(main_frame, text="Performance Metrics", padding=10)
        graph_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Create matplotlib figure
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(10, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=graph_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Configure plots
        self.ax1.set_title("Buffer Size")
        self.ax1.set_ylabel("Seconds")
        self.ax1.set_ylim(0, 20)
        self.ax1.grid(True)
        
        self.ax2.set_title("Quality and Network Speed")
        self.ax2.set_ylabel("Mbps")
        self.ax2.set_xlabel("Time")
        self.ax2.grid(True)
    
    def update_network_speed(self, value):
        self.network_speed = float(value)
        self.network_value_label.config(text=f"{self.network_speed:.1f}")
    
    def toggle_streaming(self):
        self.is_streaming = not self.is_streaming
        
        if self.is_streaming:
            self.stream_button.config(text="Stop Streaming")
            self.buffer_history = []
            self.quality_history = []
            self.network_history = []
            self.buffer_size = 0
            # Start streaming thread
            self.streaming_thread = threading.Thread(target=self.stream_simulation)
            self.streaming_thread.daemon = True
            self.streaming_thread.start()
        else:
            self.stream_button.config(text="Start Streaming")
    
    def update_ui(self):
        if self.is_streaming:
            # Update buffer display
            self.buffer_label.config(text=f"{self.buffer_size:.1f} seconds")
            self.buffer_progress['value'] = min(100, (self.buffer_size / self.target_buffer) * 100)
            
            # Update quality display
            current_quality = self.quality_levels[self.current_quality]["name"]
            self.quality_label.config(text=current_quality)
            self.video_canvas.itemconfig(self.video_quality_text, text=current_quality)
            
            # Update colors based on quality
            color_intensity = int(255 * (self.current_quality / (len(self.quality_levels) - 1)))
            quality_color = f"#{color_intensity:02x}{color_intensity:02x}ff"
            self.video_canvas.itemconfig(self.video_quality_text, fill=quality_color)
            
            # Update graphs if we have data
            if self.buffer_history:
                time_axis = list(range(len(self.buffer_history)))
                
                self.ax1.clear()
                self.ax1.plot(time_axis, self.buffer_history, 'b-')
                self.ax1.set_title("Buffer Size")
                self.ax1.set_ylabel("Seconds")
                self.ax1.set_ylim(0, self.target_buffer * 1.5)
                self.ax1.axhline(y=self.target_buffer, color='r', linestyle='--')
                self.ax1.grid(True)
                
                self.ax2.clear()
                # Plot quality as bars
                quality_values = [self.quality_levels[q]["bitrate"] for q in self.quality_history]
                self.ax2.bar(time_axis, quality_values, alpha=0.6, label="Quality (Mbps)")
                
                # Plot network speed as line
                self.ax2.plot(time_axis, self.network_history, 'r-', label="Network (Mbps)")
                
                self.ax2.set_title("Quality and Network Speed")
                self.ax2.set_ylabel("Mbps")
                self.ax2.set_xlabel("Time")
                self.ax2.legend()
                self.ax2.grid(True)
                
                self.canvas.draw()
        
        # Schedule the next update
        self.root.after(100, self.update_ui)
    
    def stream_simulation(self):
        while self.is_streaming:
            # Simulate network fluctuation if enabled
            if self.network_fluctuation_var.get():
                fluctuation = random.uniform(-2.0, 2.0)
                self.network_speed = max(0.5, min(20.0, self.network_speed + fluctuation))
                self.network_slider.set(self.network_speed)
            
            # Apply greedy approach for quality selection
            self.select_quality()
            
            # Divide and conquer: Process chunks in parallel
            self.process_chunks()
            
            # Update histories
            self.buffer_history.append(self.buffer_size)
            self.quality_history.append(self.current_quality)
            self.network_history.append(self.network_speed)
            
            # Keep histories at a reasonable size
            if len(self.buffer_history) > 100:
                self.buffer_history.pop(0)
                self.quality_history.pop(0)
                self.network_history.pop(0)
            
            # Wait before next iteration
            time.sleep(0.5)
    
    def select_quality(self):
        # Greedy approach: Select the highest quality that can be supported
        # with current network speed and buffer status
        
        # If buffer is too low, drop quality to build buffer
        if self.buffer_size < 2.0:
            self.current_quality = max(0, self.current_quality - 1)
            return
        
        # If buffer is good, find the highest quality that works with current network
        for i in range(len(self.quality_levels) - 1, -1, -1):
            # Add some headroom to avoid constant quality changes
            if self.quality_levels[i]["bitrate"] <= self.network_speed * 0.9:
                self.current_quality = i
                break
    
    def process_chunks(self):
        # Simulate chunk processing using divide and conquer
        
        # Calculate how many chunks we can process in parallel
        current_bitrate = self.quality_levels[self.current_quality]["bitrate"]
        
        # Simulate download time for a chunk
        download_time = (current_bitrate * self.chunk_size) / self.network_speed
        
        # Visualize chunk processing
        for i, label in enumerate(self.chunk_labels):
            if i == 0:
                label.config(text="■", foreground="green")
            else:
                label.config(text="□", foreground="black")
        
        # Update buffer: chunks add to buffer, playback reduces buffer
        new_buffer = self.chunk_size - download_time
        self.buffer_size = min(self.target_buffer * 1.2, self.buffer_size + new_buffer)
        
        # Simulate playback consuming buffer
        time.sleep(0.5)  # Simulate time passing
        self.buffer_size = max(0, self.buffer_size - 0.5)  # Reduce buffer by 0.5 seconds
        
        # Update chunk visualization
        for i, label in enumerate(self.chunk_labels):
            label.config(text="□", foreground="black")

def main():
    root = tk.Tk()
    app = AdaptiveVideoStreaming(root)
    root.mainloop()

if _name_ == "_main_":
    main()
