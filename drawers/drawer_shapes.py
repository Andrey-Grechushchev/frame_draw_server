# drawer_shapes.py
# UTC+5: 2025-05-11 10:45 — обновлены методы draw для поддержки контейнеров


from svgwrite.path import Path
from math import radians, sin, cos
from configs.config_log import logger

class HatchPattern:
    def __init__(self, id, angle=45, stroke="black", stroke_width=1, dasharray=None, spacing=10):
        self.id = id
        self.angle = angle % 180  # Ограничим от 0 до 179
        self.stroke = stroke
        self.stroke_width = stroke_width
        self.dasharray = dasharray
        self.spacing = spacing

    def generate(self, dwg):
        """
        Создаёт SVG pattern с вертикальной линией, повернутой на нужный угол.
        Размер pattern'а рассчитывается так, чтобы после поворота расстояние между линиями оставалось равным spacing.
        """
        angle_rad = radians(self.angle if self.angle != 0 else 0.01)
        dx = abs(self.spacing / cos(angle_rad))
        dy = abs(self.spacing / sin(angle_rad))
        size_x = min(dx, 1000)
        size_y = min(dy, 1000)

        pattern = dwg.pattern(
            id=self.id,
            size=(size_x, size_y),
            patternUnits="userSpaceOnUse",
            patternTransform=f"rotate({self.angle} 0 0)"
        )

        # Рисуем вертикальную линию (x = 0)
        line = dwg.line(
            start=(0, 0),
            end=(0, size_y),
            stroke=self.stroke,
            stroke_width=self.stroke_width
        )
        if self.dasharray:
            line.dasharray(self.dasharray)

        pattern.add(line)
        return pattern

class Line:
    def __init__(self, start, end, stroke='black', stroke_width=1, dasharray=None):
        self.start = start
        self.end = end
        self.stroke = stroke
        self.stroke_width = stroke_width
        self.dasharray = dasharray
        
    def draw(self, dwg, container):
        line = dwg.line(
            start=self.start,
            end=self.end,
            stroke=self.stroke,
            stroke_width=self.stroke_width
        )
        if self.dasharray:
            line.dasharray(self.dasharray)  
        container.add(line)


class Circle:
    def __init__(self, center, r, stroke="black", stroke_width=1, fill = "none", dasharray=None):
        self.center = center
        self.r = r
        self.stroke=stroke
        self.stroke_width = stroke_width
        self.fill_pattern = None
        self.fill = fill
        self.dasharray = dasharray

    def draw(self, dwg, container):
        circle = dwg.circle(center=self.center, r=self.r, stroke=self.stroke, 
                                 stroke_width = self.stroke_width, fill=self.fill)
        if self.dasharray:
            circle.dasharray(self.dasharray)
        container.add(circle)



class Rect:
    def __init__(self, insert, size, stroke='black', fill='none'):
        self.insert = insert
        self.size = size
        self.stroke = stroke
        self.fill = fill

    def draw(self, dwg, container):
        container.add(dwg.rect(insert=self.insert, size=self.size,
                               stroke=self.stroke, fill=self.fill))


class Ellipse:
    def __init__(self, center, r, stroke='black', fill='none'):
        self.center = center
        self.r = r  # (rx, ry)
        self.stroke = stroke
        self.fill = fill

    def draw(self, dwg, container):
        container.add(dwg.ellipse(center=self.center, r=self.r,
                               stroke=self.stroke, fill=self.fill))


class Polyline:
    def __init__(self, points, stroke_dasharray, stroke_width=1, stroke='black', fill='none'):
        self.points = points
        self.stroke_dasharray = stroke_dasharray
        self.stroke = stroke
        self.fill = fill
        self.stroke_width = stroke_width
        
    def draw(self, dwg, container):
        container.add(dwg.polyline(points=self.points, stroke_dasharray=self.stroke_dasharray,
                                   stroke=self.stroke, fill=self.fill, stroke_width = self.stroke_width))


class Polygon:
    def __init__(self, points, stroke='black', fill='none'):
        self.points = points
        self.stroke = stroke
        self.fill = fill

    def draw(self, dwg, container):
        container.add(dwg.polygon(points=self.points, stroke=self.stroke,
                                  fill=self.fill))


class Text:
    def __init__(self, text, insert, stroke_width, font_size=12, font_family='GOST type A', fill='black', rotate=None):
        self.text = text
        self.insert = insert
        self.font_size = font_size
        self.font_family = font_family
        self.fill = fill
        self.rotate = rotate
        self.stroke_width = stroke_width

    def draw(self, dwg, container):
        if self.rotate is not None:
            transform = f'rotate({self.rotate} {self.insert[0]},{self.insert[1]})'
            container.add(dwg.text(self.text, insert=self.insert, fill=self.fill,
                                   font_size=self.font_size, font_family=self.font_family,
                                   transform=transform, stroke_width = self.stroke_width))
        else:
            container.add(dwg.text(self.text, insert=self.insert, fill=self.fill,
                                   font_size=self.font_size, font_family=self.font_family, stroke_width = self.stroke_width))
   


# ------------         



def unit_vector(dx, dy):
    length = (dx**2 + dy**2)**0.5 or 1
    return dx / length, dy / length

def normal_vector(dx, dy):
    return -dy, dx

def offset_point(point, normal, distance):
    return (point[0] + normal[0] * distance, point[1] + normal[1] * distance)

class ThickPolyline:
    def __init__(self, points, thickness, stroke='black', stroke_width=1, fill=None):
        self.points = points
        self.thickness = thickness
        self.stroke = stroke
        self.stroke_width = stroke_width
        self.fill = fill

    def _compute_offset_paths(self):
        half = self.thickness / 2
        outer_path = []
        inner_path = []
        normals = []

        for i in range(len(self.points) - 1):
            dx = self.points[i + 1][0] - self.points[i][0]
            dy = self.points[i + 1][1] - self.points[i][1]
            ux, uy = unit_vector(dx, dy)
            nx, ny = unit_vector(*normal_vector(ux, uy))
            normals.append((nx, ny))

        for i, point in enumerate(self.points):
            if i == 0:
                nx, ny = normals[i]
            elif i == len(self.points) - 1:
                nx, ny = normals[i - 1]
            else:
                nx1, ny1 = normals[i - 1]
                nx2, ny2 = normals[i]
                nx, ny = unit_vector(nx1 + nx2, ny1 + ny2)

            outer_path.append(offset_point(point, (nx, ny), half))
            inner_path.append(offset_point(point, (nx, ny), -half))

        return outer_path, inner_path, normals

    def _add_round_cap(self, path, center, direction, reverse=False):
        radius = self.thickness / 2
        dx, dy = unit_vector(*direction)
        nx, ny = normal_vector(dx, dy)

        if reverse:
            start = offset_point(center, (nx, ny), -radius)
            end = offset_point(center, (nx, ny), radius)
            path.push('L', start)
            path.push('A', (radius, radius, 0, 0, 0, end[0], end[1]))
        else:
            start = offset_point(center, (nx, ny), radius)
            end = offset_point(center, (nx, ny), -radius)
            path.push('L', start)
            path.push('A', (radius, radius, 0, 0, 0, end[0], end[1]))

    def get_path(self):
        outer, inner, _ = self._compute_offset_paths()
        if not outer:
            return Path(fill='none', stroke=self.stroke, stroke_width=self.stroke_width)

        path = Path(fill='none', stroke=self.stroke, stroke_width=self.stroke_width)
        path.push('M', outer[0])

        for i in range(1, len(outer)):
            path.push('L', outer[i])

        self._add_round_cap(path, self.points[-1], (
            self.points[-1][0] - self.points[-2][0],
            self.points[-1][1] - self.points[-2][1]), reverse=False)

        for pt in reversed(inner):
            path.push('L', pt)

        self._add_round_cap(path, self.points[0], (
            self.points[1][0] - self.points[0][0],
            self.points[1][1] - self.points[0][1]), reverse=True)

        path.push('Z')
        return path
    
    def _create_hatch_pattern(self, dwg, angle=45, size=6, stroke='black', stroke_width=1):
        pattern_id = f"hatch_{angle}"
        pattern = dwg.pattern(
            id=pattern_id,
            size=(size, size),
            patternUnits="userSpaceOnUse",
            patternTransform=f"rotate({angle})"
        )
        pattern.add(dwg.line(start=(0, 0), end=(0, size), stroke=stroke, stroke_width=stroke_width))
        dwg.defs.add(pattern)
        return f"url(#{pattern_id})"

    def draw(self, dwg, container):
        if self.fill:
            fill_path = self.get_fill_path(dwg)
            container.add(fill_path)

        path = self.get_path()
        container.add(path)

    def get_fill_path(self, dwg=None):
        path = self.get_path()

        if self.fill == "none":
            path.fill("none")
        elif self.fill.startswith("hatch_") and dwg is not None:
            try:
                angle = int(self.fill.split("_")[1])
            except ValueError:
                angle = 45
            pattern_url = self._create_hatch_pattern(dwg, angle=angle)
            path.fill(pattern_url)
        else:
            path.fill(self.fill)

        path.stroke("none")
        return path

# ------------
