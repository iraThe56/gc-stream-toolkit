"""
Animation of tidal stream evolution from HDF5 simulation data.
"""

import h5py
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


class StreamAnimator:
    """
    Creates animations from HDF5 tidal stream simulation files.
    Supports single or multiple streams for comparative analysis.

    Examples
    --------
    # Single stream
    StreamAnimator("simulation.h5").animate().save("stream.gif")

    # Multiple streams with auto-configuration
    StreamAnimator(["ngc6569.h5", "pal5.h5"]).animate().save("comparison.gif")

    # Custom configuration
    StreamAnimator(["ngc6569.h5", "pal5.h5"]).configure(
        cluster_colors=['red', 'blue'],
        cluster_labels=['NGC 6569', 'Pal 5'],
        stream_colors=['pink', 'cyan'],
        fps=60
    ).animate().save("comparison.gif")
    """

    def __init__(self, filenames):
        self.filenames = [filenames] if isinstance(filenames, str) else filenames
        self.n_streams = len(self.filenames)
        self._set_defaults()
        self._load_data()

    def _set_defaults(self):
        """Set sensible defaults for all configuration options."""
        # Animation parameters
        self.fps = 10
        self.interval = 100
        self.figure_size = (10, 8)
        self.repeat = True

        # Default color palette that cycles
        default_colors = ['red', 'blue', 'green', 'orange', 'purple', 'cyan',
                         'magenta', 'brown', 'pink', 'gray', 'olive', 'navy']

        # Auto-assign colors for each stream
        self.cluster_colors = [default_colors[i % len(default_colors)] for i in range(self.n_streams)]
        self.stream_colors = [default_colors[i % len(default_colors)] for i in range(self.n_streams)]

        # Auto-generate labels from filenames
        self.cluster_labels = [self._extract_cluster_name(f) for f in self.filenames]

        # Individual stream styling (same for all streams by default)
        self.cluster_size = 100
        self.cluster_marker = '*'
        self.stream_size = 1
        self.stream_alpha = 0.6

        # Axis styling
        self.axis_margin = 1.0
        self.show_legend = True
        self.title_template = 'Tidal Stream Evolution\nTime: {time:.1f} Myr'

        # Output
        self.animation = None

    def _extract_cluster_name(self, filename):
        """Extract cluster name from filename for auto-labeling."""
        import os
        base = os.path.basename(filename)
        name = base.replace('.h5', '').replace('_stream_evolution', '')
        return name.upper()

    def _load_data(self):
        """Load and synchronize data from all HDF5 files."""
        self.streams_data = []
        all_times = []

        # Load each file
        for filename in self.filenames:
            with h5py.File(filename, 'r') as file:
                stream_data = {
                    'cluster_positions': file['nbody/pos'][:],
                    'stream_positions': file['stream/pos'][:],
                    'times': file['nbody/time'][:]
                }
                self.streams_data.append(stream_data)
                all_times.append(stream_data['times'])

        # Create master timeline
        self._create_master_timeline(all_times)
        self._sync_all_streams()
        self._calculate_axis_limits()

    def _create_master_timeline(self, all_times):
        """Create a master timeline that spans all simulations."""
        # Find overall time bounds
        earliest_time = min(times.min() for times in all_times)
        latest_time = max(times.max() for times in all_times)

        # Find finest timestep
        timesteps = []
        for times in all_times:
            if len(times) > 1:
                dt = abs(times[1] - times[0])
                timesteps.append(dt)

        finest_dt = min(timesteps) if timesteps else 0.5

        # Create master timeline
        n_steps = int((latest_time - earliest_time) / finest_dt) + 1
        self.master_time = np.linspace(earliest_time, latest_time, n_steps)
        self.n_timesteps = len(self.master_time)

    def _sync_all_streams(self):
        """Synchronize all streams to master timeline."""
        self.synced_cluster_positions = []
        self.synced_stream_positions = []

        for stream_data in self.streams_data:
            # Interpolate cluster positions to master timeline
            cluster_synced = self._interpolate_to_master(
                stream_data['times'],
                stream_data['cluster_positions']
            )

            # Interpolate stream positions to master timeline
            stream_synced = self._interpolate_to_master(
                stream_data['times'],
                stream_data['stream_positions']
            )

            self.synced_cluster_positions.append(cluster_synced)
            self.synced_stream_positions.append(stream_synced)

    def _interpolate_to_master(self, original_times, positions):
        """Interpolate position data to master timeline."""
        # Handle case where master time extends beyond original simulation
        synced_positions = np.full((3, self.n_timesteps, positions.shape[2]), np.nan)

        # Find overlap region
        start_idx = np.searchsorted(self.master_time, original_times.min())
        end_idx = np.searchsorted(self.master_time, original_times.max()) + 1
        end_idx = min(end_idx, self.n_timesteps)

        if start_idx < end_idx:
            overlap_times = self.master_time[start_idx:end_idx]

            # Interpolate each coordinate and particle
            for coord in range(3):
                for particle in range(positions.shape[2]):
                    synced_positions[coord, start_idx:end_idx, particle] = np.interp(
                        overlap_times, original_times, positions[coord, :, particle]
                    )

        return synced_positions

    def _calculate_axis_limits(self):
        """Calculate axis limits encompassing all streams."""
        all_positions = []

        # Collect all valid positions from all streams
        for i in range(self.n_streams):
            cluster_pos = self.synced_cluster_positions[i].reshape(3, -1)
            stream_pos = self.synced_stream_positions[i].reshape(3, -1)
            all_positions.append(np.concatenate([cluster_pos, stream_pos], axis=1))

        # Combine all streams
        combined_positions = np.concatenate(all_positions, axis=1)
        valid_positions = combined_positions[:, ~np.isnan(combined_positions).any(axis=0)]

        if valid_positions.size > 0:
            self.x_limits = [
                valid_positions[0].min() - self.axis_margin,
                valid_positions[0].max() + self.axis_margin
            ]
            self.y_limits = [
                valid_positions[1].min() - self.axis_margin,
                valid_positions[1].max() + self.axis_margin
            ]
            self.z_limits = [
                valid_positions[2].min() - self.axis_margin,
                valid_positions[2].max() + self.axis_margin
            ]
        else:
            # Fallback if no valid data
            self.x_limits = [-10, 10]
            self.y_limits = [-10, 10]
            self.z_limits = [-10, 10]

    def configure(self, **kwargs):
        """Configure all animation settings."""
        # Animation parameters
        if 'fps' in kwargs: self.fps = kwargs['fps']
        if 'interval' in kwargs: self.interval = kwargs['interval']
        if 'figure_size' in kwargs: self.figure_size = kwargs['figure_size']
        if 'repeat' in kwargs: self.repeat = kwargs['repeat']

        # Multi-stream parameters (lists)
        if 'cluster_colors' in kwargs: self.cluster_colors = kwargs['cluster_colors']
        if 'stream_colors' in kwargs: self.stream_colors = kwargs['stream_colors']
        if 'cluster_labels' in kwargs: self.cluster_labels = kwargs['cluster_labels']

        # Single stream parameters (applied to all)
        if 'cluster_size' in kwargs: self.cluster_size = kwargs['cluster_size']
        if 'cluster_marker' in kwargs: self.cluster_marker = kwargs['cluster_marker']
        if 'stream_size' in kwargs: self.stream_size = kwargs['stream_size']
        if 'stream_alpha' in kwargs: self.stream_alpha = kwargs['stream_alpha']

        # Axis and display
        if 'axis_margin' in kwargs:
            self.axis_margin = kwargs['axis_margin']
            self._calculate_axis_limits()
        if 'show_legend' in kwargs: self.show_legend = kwargs['show_legend']
        if 'title' in kwargs: self.title_template = kwargs['title']
        if 'x_limits' in kwargs: self.x_limits = kwargs['x_limits']
        if 'y_limits' in kwargs: self.y_limits = kwargs['y_limits']
        if 'z_limits' in kwargs: self.z_limits = kwargs['z_limits']

        return self

    def set(self, **kwargs):
        """Shorter alias for configure()."""
        return self.configure(**kwargs)

    def matplotlib_config(self, **kwargs):
        """Direct passthrough to matplotlib 3D axis configuration."""
        self.view_kwargs.update(kwargs)
        return self

    def animate(self):
        """Create the animation object."""
        self.figure = plt.figure(figsize=self.figure_size)
        self.axis = self.figure.add_subplot(111, projection='3d')

        self.animation = FuncAnimation(
            self.figure,
            self._animate_frame,
            frames=self.n_timesteps,
            interval=self.interval,
            blit=False,
            repeat=self.repeat
        )

        return self

    def _animate_frame(self, frame):
        """Render a single animation frame with all streams."""
        self.axis.clear()

        # Plot each stream
        for i in range(self.n_streams):
            self._plot_single_stream(frame, i)

        # Set consistent view
        self.axis.set_xlim(self.x_limits)
        self.axis.set_ylim(self.y_limits)
        self.axis.set_zlim(self.z_limits)
        self.axis.set_xlabel('X [kpc]')
        self.axis.set_ylabel('Y [kpc]')
        self.axis.set_zlabel('Z [kpc]')

        # Add title and legend
        current_time = self.master_time[frame]
        self.axis.set_title(self.title_template.format(time=current_time))

        if self.show_legend:
            self.axis.legend()

    def _plot_single_stream(self, frame, stream_idx):
        """Plot cluster and stream for a single simulation at given frame."""
        # Get cluster position
        cluster_pos = self.synced_cluster_positions[stream_idx][:, frame, 0]

        # Get stream positions
        stream_pos = self.synced_stream_positions[stream_idx][:, frame, :]

        # Only plot if not NaN (stream exists at this time)
        if not np.isnan(cluster_pos).any():
            # Plot cluster
            self.axis.scatter(
                [cluster_pos[0]], [cluster_pos[1]], [cluster_pos[2]],
                s=self.cluster_size,
                c=self.cluster_colors[stream_idx],
                marker=self.cluster_marker,
                label=self.cluster_labels[stream_idx]
            )

            # Plot stream particles
            valid_stream = ~np.isnan(stream_pos[0])
            if np.any(valid_stream):
                self.axis.scatter(
                    stream_pos[0, valid_stream],
                    stream_pos[1, valid_stream],
                    stream_pos[2, valid_stream],
                    s=self.stream_size,
                    c=self.stream_colors[stream_idx],
                    alpha=self.stream_alpha,
                    label=f'{self.cluster_labels[stream_idx]} Stream'
                )

    def save(self, filename):
        """Save animation to file."""
        if self.animation is None:
            raise RuntimeError("Must call animate() before save()")

        # Determine writer from filename extension
        if filename.endswith('.mp4'):
            writer = 'ffmpeg'
        elif filename.endswith('.gif'):
            writer = 'pillow'
        else:
            writer = 'pillow'

        print(f"Saving animation to {filename}...")
        self.animation.save(filename, writer=writer, fps=self.fps)
        print("Animation saved!")

        return self

    def show(self):
        """Display animation in notebook."""
        if self.animation is None:
            raise RuntimeError("Must call animate() before show()")

        plt.show()
        return self


# Convenience function for one-liner usage
def animate_stream(filenames):
    """Create StreamAnimator object from filename(s)."""
    return StreamAnimator(filenames)