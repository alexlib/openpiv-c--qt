#pragma once

#include "map_sinc.impl.h"

#include <cstdint>
#include <type_traits>

#include "core/vector_field.h"
#include "core/image.h"
#include "core/image_type_traits.h"
#include "core/pixel_types.h"
#include "interp_common.impl.h"

namespace openpiv::interp
{
    using namespace openpiv::core;
    
    inline double sinc_weighting(double x);


    template < template <typename> class ImageT,
               typename ContainedT,
               typename ValueT = typename ContainedT::value_t,
               typename OutT = image<g<ValueT>>,
               typename = typename std::enable_if_t<
                   is_imagetype_v<ImageT<ContainedT>> &&
                   is_real_mono_pixeltype_v<ContainedT> &&
                   std::is_same_v<ValueT, double>
                   >
                >
    void sinc_interp2d(
        const core::image<ContainedT>& src,
        const core::grid_coords& mappings,
        core::image<ContainedT>& out,
        int kernel_half_size
    )
    {
        const int width  = src.width();
        const int height = src.height();

        out.resize(mappings.size());

        for (uint32_t y = 0; y < mappings.height(); ++y)
        {
            for (uint32_t x = 0; x < mappings.width(); ++x)
            {
                const auto& point_xy = mappings[{x,y}];

                const double bx = point_xy[0];
                const double by = point_xy[1];

                const int xn = static_cast<int>(bx);
                const int yn = static_cast<int>(by);

                double value = 0.0;

                for (int j = yn - kernel_half_size; j <= yn + kernel_half_size; ++j)
                {
                    const int jj = mirror_index(j, height);

                    const double dy = j - by;
                    const double sy = sinc_weighting(dy);

                    const ContainedT* row = src.line(jj);

                    for (int i = xn - kernel_half_size; i <= xn + kernel_half_size; ++i)
                    {
                        const int ii = mirror_index(i, width);

                        const double dx = i - bx;
                        const double sx = sinc_weighting(dx);

                        value += row[ii] * sx * sy;
                    }
                }

                out[{x,y}] = static_cast<ContainedT>(value);
            }
        }
    }
}